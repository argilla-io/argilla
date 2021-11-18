from typing import Any, ClassVar, Dict, Iterable, List, Set, Tuple

from pydantic import BaseModel, Field

from rubrix.server.commons.es_helpers import aggregations
from rubrix.server.tasks.commons.dao import extends_index_properties
from rubrix.server.tasks.commons.metrics import CommonTasksMetrics
from rubrix.server.tasks.commons.metrics.model.base import (
    BaseMetric,
    BaseTaskMetrics,
    ElasticsearchMetric,
    NestedPathElasticsearchMetric,
    PythonMetric,
)
from rubrix.server.tasks.token_classification import (
    EntitySpan,
    TokenClassificationRecord,
)


class TokensLength(ElasticsearchMetric):
    """
    Summarizes the tokens length metric into an histogram

    Attributes:
    -----------
    length_field:
        The elasticsearch field where tokens length is stored
    """

    length_field: str

    def aggregation_request(self, interval: int) -> Dict[str, Any]:
        return {
            self.id: aggregations.histogram_aggregation(
                self.length_field, interval=interval or 1
            )
        }


_DEFAULT_MAX_ENTITY_BUCKET = 1000


class EntityLabels(NestedPathElasticsearchMetric):
    """
    Computes the entity labels distribution

    Attributes:
    -----------
    labels_field:
        The elasticsearch field where tags are stored
    """

    labels_field: str

    def inner_aggregation(self, size: int) -> Dict[str, Any]:
        return {
            "labels": aggregations.terms_aggregation(
                self.compound_nested_field(self.labels_field),
                size=size or _DEFAULT_MAX_ENTITY_BUCKET,
            )
        }


class EntityDensity(NestedPathElasticsearchMetric):
    """Summarizes the entity density metric into an histogram"""

    density_field: str

    def inner_aggregation(self, interval: float) -> Dict[str, Any]:
        return {
            "density": aggregations.histogram_aggregation(
                field_name=self.compound_nested_field(self.density_field),
                interval=interval or 0.01,
            )
        }


class MentionLength(NestedPathElasticsearchMetric):
    """Summarizes the mention length into an histogram"""

    length_field: str

    def inner_aggregation(self, interval: int) -> Dict[str, Any]:
        return {
            "mention_length": aggregations.histogram_aggregation(
                self.compound_nested_field(self.length_field), interval=interval or 1
            )
        }


class EntityCapitalness(NestedPathElasticsearchMetric):
    """Computes the mention capitalness distribution"""

    capitalness_field: str

    def inner_aggregation(self) -> Dict[str, Any]:
        return {
            "capitalness": aggregations.terms_aggregation(
                self.compound_nested_field(self.capitalness_field),
                size=4,  # The number of capitalness choices
            )
        }


class EntityConsistency(NestedPathElasticsearchMetric):
    """Computes the entity consistency distribution"""

    mention_field: str
    labels_field: str

    def inner_aggregation(
        self,
        size: int,
        interval: int = 2,
        entity_size: int = _DEFAULT_MAX_ENTITY_BUCKET,
    ) -> Dict[str, Any]:
        size = size or 50
        interval = int(max(interval or 2, 2))
        return {
            "consistency": {
                **aggregations.terms_aggregation(
                    self.compound_nested_field(self.mention_field), size=size
                ),
                "aggs": {
                    "entities": aggregations.terms_aggregation(
                        self.compound_nested_field(self.labels_field), size=entity_size
                    ),
                    "count": {
                        "cardinality": {
                            "field": self.compound_nested_field(self.labels_field)
                        }
                    },
                    "entities_variability_filter": {
                        "bucket_selector": {
                            "buckets_path": {"numLabels": "count"},
                            "script": f"params.numLabels >= {interval}",
                        }
                    },
                    "sortby_entities_count": {
                        "bucket_sort": {
                            "sort": [{"count": {"order": "desc"}}],
                            "size": size,
                        }
                    },
                },
            }
        }

    def aggregation_result(self, aggregation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Simplifies the aggregation result sorting by worst mention consistency"""
        result = [
            {
                "mention": mention,
                "entities": [
                    {"label": entity, "count": count}
                    for entity, count in mention_aggs["entities"].items()
                ],
            }
            for mention, mention_aggs in aggregation_result.items()
        ]
        # TODO: filter by entities threshold
        result.sort(key=lambda m: len(m["entities"]), reverse=True)
        return {"mentions": result}


class F1Metric(PythonMetric[TokenClassificationRecord]):
    """The F1 metric based on entity-level.

    We follow the convention of `CoNLL 2003 <https://aclanthology.org/W03-0419/>`_, where:
    `"precision is the percentage of named entities found by the learning system that are correct.
    Recall is the percentage of named entities present in the corpus that are found by the system.
    A named entity is correct only if it is an exact match (...).”`
    """

    def apply(self, records: Iterable[TokenClassificationRecord]) -> Dict[str, Any]:
        # store entities per label in dicts
        predicted_entities = {}
        annotated_entities = {}

        # extract entities per label to dicts
        for rec in records:
            if rec.prediction:
                self._add_entities_to_dict(rec.prediction.entities, predicted_entities)
            if rec.annotation:
                self._add_entities_to_dict(rec.annotation.entities, annotated_entities)

        # store precision, recall, and f1 per label
        per_label_metrics = {}

        annotated_total, predicted_total, correct_total = 0, 0, 0
        precision_macro, recall_macro = 0, 0
        for label, annotated in annotated_entities.items():
            predicted = predicted_entities.get(label, set())
            correct = len(annotated & predicted)

            # safe divides are used to cover the 0/0 cases
            precision = self._safe_divide(correct, len(predicted))
            recall = self._safe_divide(correct, len(annotated))
            per_label_metrics.update(
                {
                    f"{label}_precision": precision,
                    f"{label}_recall": recall,
                    f"{label}_f1": self._safe_divide(
                        2 * precision * recall, precision + recall
                    ),
                }
            )

            annotated_total += len(annotated)
            predicted_total += len(predicted)
            correct_total += correct

            precision_macro += precision / len(annotated_entities)
            recall_macro += recall / len(annotated_entities)

        # store macro and micro averaged precision, recall and f1
        averaged_metrics = {
            "precision_macro": precision_macro,
            "recall_macro": recall_macro,
            "f1_macro": self._safe_divide(
                2 * precision_macro * recall_macro, precision_macro + recall_macro
            ),
        }

        precision_micro = self._safe_divide(correct_total, predicted_total)
        recall_micro = self._safe_divide(correct_total, annotated_total)
        averaged_metrics.update(
            {
                "precision_micro": precision_micro,
                "recall_micro": recall_micro,
                "f1_micro": self._safe_divide(
                    2 * precision_micro * recall_micro, precision_micro + recall_micro
                ),
            }
        )

        return {**averaged_metrics, **per_label_metrics}

    @staticmethod
    def _add_entities_to_dict(
        entities: List[EntitySpan], dictionary: Dict[str, Set[Tuple[int, int]]]
    ):
        """Helper function for the apply method."""
        for ent in entities:
            try:
                dictionary[ent.label].add((ent.start, ent.end))
            except KeyError:
                dictionary[ent.label] = {(ent.start, ent.end)}

    @staticmethod
    def _safe_divide(numerator, denominator):
        """Helper function for the apply method."""
        try:
            return numerator / denominator
        except ZeroDivisionError:
            return 0


class TokenClassificationMetrics(BaseTaskMetrics[TokenClassificationRecord]):
    """Configured metrics for token classification"""

    _PREDICTED_MENTIONS_NAMESPACE = "metrics.predicted.mentions"
    _ANNOTATED_MENTIONS_NAMESPACE = "metrics.annotated.mentions"

    class MentionMetrics(BaseModel):
        """Mention metrics model"""

        value: str
        label: str
        score: float = Field(ge=0.0)
        capitalness: str = Field(...)
        density: float = Field(ge=0.0)
        tokens_length: int = Field(g=0)
        chars_length: int = Field(g=0)

    @staticmethod
    def mentions_metrics(
        mentions: List[Tuple[str, EntitySpan]],
        tokens: List[str],
        chars2tokens: Dict[int, int],
    ) -> List[MentionMetrics]:
        """Given a list of mentions with its entity spans, Compute all required metrics"""

        def mention_capitalness(mention: str) -> str:
            """Compute mention capitalness"""
            mention = mention.strip()
            if mention.upper() == mention:
                return "UPPER"
            if mention.lower() == mention:
                return "LOWER"
            if mention[0].isupper():
                return "FIRST"
            return "MIDDLE"

        def mention_tokens_length(
            entity: EntitySpan, chars2token_map: Dict[int, int]
        ) -> int:
            """Compute mention tokens length"""
            return len(
                set(
                    [
                        token_idx
                        for i in range(entity.start, entity.end)
                        for token_idx in [chars2token_map.get(i)]
                        if token_idx is not None
                    ]
                )
            )

        def mention_density(mention_length: int, tokens_length: int) -> float:
            """Compute mention density"""
            return (1.0 * mention_length) / tokens_length

        return [
            TokenClassificationMetrics.MentionMetrics(
                value=mention,
                label=entity.label,
                score=entity.score,
                capitalness=mention_capitalness(mention),
                density=mention_density(_tokens_length, tokens_length=len(tokens)),
                tokens_length=_tokens_length,
                chars_length=len(mention),
            )
            for mention, entity in mentions
            for _tokens_length in [
                mention_tokens_length(entity, chars2tokens),
            ]
        ]

    @staticmethod
    def build_chars2tokens_map(record: TokenClassificationRecord) -> Dict[int, int]:
        """
        Build the mapping between text characters and where belongs to.

        For example, ``chars2tokens_map.get(i)`` value is the
        token id where char i is contained (if any).

        Out-of-token characters won't be included in this map,
        so access should be using ``chars2tokens_map.get(i)``
        instead of ``chars2tokens_map[i]``.

        """

        chars_map = {}
        current_token = 0
        current_token_char_start = 0
        for idx, char in enumerate(record.text):
            relative_idx = idx - current_token_char_start
            if (
                relative_idx < len(record.tokens[current_token])
                and char == record.tokens[current_token][relative_idx]
            ):
                chars_map[idx] = current_token
            elif (
                current_token + 1 < len(record.tokens)
                and relative_idx >= len(record.tokens[current_token])
                and char == record.tokens[current_token + 1][0]
            ):
                current_token += 1
                current_token_char_start += relative_idx
                chars_map[idx] = current_token
        return chars_map

    @classmethod
    def configure_es_index(cls):
        """Configure mentions as nested properties"""

        def resolve_type(info):
            the_type = info.get("type")
            if the_type == "number":
                return "float"
            if the_type == "integer":
                return "integer"
            return "keyword"

        mentions_configuration = {
            "type": "nested",
            "include_in_root": True,
            "properties": {
                key: {"type": resolve_type(info)}
                for key, info in cls.MentionMetrics.schema()["properties"].items()
            },
        }
        extends_index_properties(
            {
                cls._PREDICTED_MENTIONS_NAMESPACE: mentions_configuration,
                cls._ANNOTATED_MENTIONS_NAMESPACE: mentions_configuration,
            }
        )

    @classmethod
    def record_metrics(cls, record: TokenClassificationRecord) -> Dict[str, Any]:
        """Compute metrics at record level"""
        chars2tokens = cls.build_chars2tokens_map(record)

        return {
            "tokens_length": len(record.tokens),
            "predicted": {
                "mentions": cls.mentions_metrics(
                    mentions=record.predicted_mentions(),
                    tokens=record.tokens,
                    chars2tokens=chars2tokens,
                )
            },
            "annotated": {
                "mentions": cls.mentions_metrics(
                    mentions=record.annotated_mentions(),
                    tokens=record.tokens,
                    chars2tokens=chars2tokens,
                )
            },
        }

    _PREDICTED_METRICS = [
        EntityDensity(
            id="predicted_entity_density",
            name="Mention entity density for predictions",
            description="Computes the ratio between the number of all entity tokens and tokens in the text",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            density_field="density",
        ),
        EntityLabels(
            id="predicted_entity_labels",
            name="Predicted entity labels",
            description="Predicted entity labels distribution",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            labels_field="label",
        ),
        EntityCapitalness(
            id="predicted_entity_capitalness",
            name="Mention entity capitalness for predictions",
            description="Compute capitalization information of predicted entity mentions",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            capitalness_field="capitalness",
        ),
        MentionLength(
            id="predicted_mention_token_length",
            name="Predicted mention tokens length",
            description="Computes the length of the predicted entity mention measured in number of tokens",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            length_field="tokens_length",
        ),
        MentionLength(
            id="predicted_mention_char_length",
            name="Predicted mention characters length",
            description="Computes the length of the predicted entity mention measured in number of tokens",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            length_field="chars_length",
        ),
        EntityConsistency(
            id="predicted_entity_consistency",
            name="Entity label consistency for predictions",
            description="Computes entity label variability for top-k predicted entity mentions",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            mention_field="value",
            labels_field="label",
        ),
    ]

    _ANNOTATED_METRICS = [
        EntityDensity(
            id="annotated_entity_density",
            name="Mention entity density for annotations",
            description="Computes the ratio between the number of all entity tokens and tokens in the text",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
            density_field="density",
        ),
        EntityLabels(
            id="annotated_entity_labels",
            name="Annotated entity labels",
            description="Annotated Entity labels distribution",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
            labels_field="label",
        ),
        EntityCapitalness(
            id="annotated_entity_capitalness",
            name="Mention entity capitalness for annotations",
            description="Compute capitalization information of annotated entity mentions",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
            capitalness_field="capitalness",
        ),
        MentionLength(
            id="annotated_mention_token_length",
            name="Annotated mention tokens length",
            description="Computes the length of the entity mention measured in number of tokens",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
            length_field="tokens_length",
        ),
        MentionLength(
            id="annotated_mention_char_length",
            name="Annotated mention characters length",
            description="Computes the length of the entity mention measured in number of tokens",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
            length_field="chars_length",
        ),
        EntityConsistency(
            id="annotated_entity_consistency",
            name="Entity label consistency for annotations",
            description="Computes entity label variability for top-k annotated entity mentions",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
            mention_field="value",
            labels_field="label",
        ),
    ]

    metrics: ClassVar[List[BaseMetric]] = CommonTasksMetrics.metrics + [
        TokensLength(
            id="tokens_length",
            name="Tokens length",
            description="Computes the text length distribution measured in number of tokens",
            length_field="metrics.tokens_length",
        ),
        *_PREDICTED_METRICS,
        *_ANNOTATED_METRICS,
        F1Metric(
            id="F1",
            name="F1 Metric based on entity-level",
            description="F1 metrics based on entity-level (averaged and per label), "
            "where only exact matches count (CoNNL 2003).",
        ),
    ]
