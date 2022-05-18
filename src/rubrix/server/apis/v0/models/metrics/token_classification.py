from typing import Any, ClassVar, Dict, Iterable, List, Optional, Set, Tuple

from pydantic import BaseModel, Field

from rubrix.server.apis.v0.models.metrics.base import (
    BaseMetric,
    ElasticsearchMetric,
    HistogramAggregation,
    NestedHistogramAggregation,
    NestedPathElasticsearchMetric,
    NestedTermsAggregation,
    PythonMetric,
    TermsAggregation,
)
from rubrix.server.apis.v0.models.metrics.commons import CommonTasksMetrics
from rubrix.server.apis.v0.models.token_classification import (
    EntitySpan,
    TokenClassificationRecord,
)
from rubrix.server.elasticseach.query_helpers import aggregations


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


class MentionsByEntityDistribution(NestedPathElasticsearchMetric):
    def inner_aggregation(self):
        return {
            self.id: aggregations.bidimentional_terms_aggregations(
                field_name_x=f"{self.nested_path}.label",
                field_name_y=f"{self.nested_path}.value",
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


class DatasetLabels(PythonMetric):
    id: str = Field("dataset_labels", const=True)
    name: str = Field("The dataset entity labels", const=True)
    max_processed_records: int = 10000

    def apply(self, records: Iterable[TokenClassificationRecord]) -> Dict[str, Any]:
        ds_labels = set()

        for _ in range(
            0, self.max_processed_records
        ):  # Only a few of records will be parsed
            record: TokenClassificationRecord = next(records, None)
            if record is None:
                break

            if record.annotation:
                ds_labels.update(
                    [entity.label for entity in record.annotation.entities]
                )
            if record.prediction:
                ds_labels.update(
                    [entity.label for entity in record.prediction.entities]
                )
        return {"labels": ds_labels or []}


class MentionMetrics(BaseModel):
    """Mention metrics model"""

    value: str
    label: str
    score: float = Field(ge=0.0)
    capitalness: Optional[str] = Field(None)
    density: float = Field(ge=0.0)
    tokens_length: int = Field(g=0)
    chars_length: int = Field(g=0)


class TokenTagMetrics(BaseModel):
    value: str
    tag: str


class TokenMetrics(BaseModel):
    """
    Token metrics stored in elasticsearch for token classification

    Attributes
        idx: The token index in sentence
        value: The token textual value
        char_start: The token character start position in sentence
        char_end: The token character end position in sentence
        score: Token score info
        tag: Token tag info. Deprecated: Use metrics.predicted.tags or metrics.annotated.tags instead
        custom: extra token level info
    """

    idx: int
    value: str
    char_start: int
    char_end: int
    length: int
    capitalness: Optional[str] = None
    score: Optional[float] = None
    tag: Optional[str] = None  # TODO: remove!
    custom: Dict[str, Any] = None


class TokenClassificationMetrics(CommonTasksMetrics[TokenClassificationRecord]):
    """Configured metrics for token classification"""

    _PREDICTED_NAMESPACE = "metrics.predicted"
    _ANNOTATED_NAMESPACE = "metrics.annotated"

    _PREDICTED_MENTIONS_NAMESPACE = f"{_PREDICTED_NAMESPACE}.mentions"
    _ANNOTATED_MENTIONS_NAMESPACE = f"{_ANNOTATED_NAMESPACE}.mentions"

    _PREDICTED_TAGS_NAMESPACE = f"{_PREDICTED_NAMESPACE}.tags"
    _ANNOTATED_TAGS_NAMESPACE = f"{_ANNOTATED_NAMESPACE}.tags"

    _TOKENS_NAMESPACE = "metrics.tokens"

    @staticmethod
    def density(value: int, sentence_length: int) -> float:
        """Compute the string density over a sentence"""
        return value / sentence_length

    @staticmethod
    def capitalness(value: str) -> Optional[str]:
        """Compute capitalness for a string value"""
        value = value.strip()
        if not value:
            return None
        if value.isupper():
            return "UPPER"
        if value.islower():
            return "LOWER"
        if value[0].isupper():
            return "FIRST"
        if any([c.isupper() for c in value[1:]]):
            return "MIDDLE"
        return None

    @staticmethod
    def mentions_metrics(
        record: TokenClassificationRecord, mentions: List[Tuple[str, EntitySpan]]
    ):
        def mention_tokens_length(entity: EntitySpan) -> int:
            """Compute mention tokens length"""
            return len(
                set(
                    [
                        token_idx
                        for i in range(entity.start, entity.end)
                        for token_idx in [record.char_id2token_id(i)]
                        if token_idx is not None
                    ]
                )
            )

        return [
            MentionMetrics(
                value=mention,
                label=entity.label,
                score=entity.score,
                capitalness=TokenClassificationMetrics.capitalness(mention),
                density=TokenClassificationMetrics.density(
                    _tokens_length, sentence_length=len(record.tokens)
                ),
                tokens_length=_tokens_length,
                chars_length=len(mention),
            )
            for mention, entity in mentions
            for _tokens_length in [
                mention_tokens_length(entity),
            ]
        ]

    @classmethod
    def build_tokens_metrics(
        cls, record: TokenClassificationRecord, tags: Optional[List[str]] = None
    ) -> List[TokenMetrics]:

        return [
            TokenMetrics(
                idx=token_idx,
                value=token_value,
                char_start=char_start,
                char_end=char_end,
                capitalness=cls.capitalness(token_value),
                length=1 + (char_end - char_start),
                tag=tags[token_idx] if tags else None,
            )
            for token_idx, token_value in enumerate(record.tokens)
            for char_start, char_end in [record.token_span(token_idx)]
        ]

    @classmethod
    def record_metrics(cls, record: TokenClassificationRecord) -> Dict[str, Any]:
        """Compute metrics at record level"""
        base_metrics = super(TokenClassificationMetrics, cls).record_metrics(record)

        annotated_tags = record.annotated_iob_tags() or []
        predicted_tags = record.predicted_iob_tags() or []

        tokens_metrics = cls.build_tokens_metrics(
            record, predicted_tags or annotated_tags
        )
        return {
            **base_metrics,
            "tokens": tokens_metrics,
            "tokens_length": len(record.tokens),
            "predicted": {
                "mentions": cls.mentions_metrics(record, record.predicted_mentions()),
                "tags": [
                    TokenTagMetrics(tag=tag, value=token)
                    for tag, token in zip(predicted_tags, record.tokens)
                ],
            },
            "annotated": {
                "mentions": cls.mentions_metrics(record, record.annotated_mentions()),
                "tags": [
                    TokenTagMetrics(tag=tag, value=token)
                    for tag, token in zip(annotated_tags, record.tokens)
                ],
            },
        }

    _TOKENS_METRICS = [
        TokensLength(
            id="tokens_length",
            name="Tokens length",
            description="Computes the text length distribution measured in number of tokens",
            length_field="metrics.tokens_length",
        ),
        NestedTermsAggregation(
            id="token_frequency",
            name="Tokens frequency distribution",
            nested_path=_TOKENS_NAMESPACE,
            terms=TermsAggregation(
                id="frequency",
                field="value",
                name="",
            ),
        ),
        NestedHistogramAggregation(
            id="token_length",
            name="Token length distribution",
            nested_path=_TOKENS_NAMESPACE,
            description="Computes token length distribution in number of characters",
            histogram=HistogramAggregation(
                id="length",
                field="length",
                name="",
                fixed_interval=1,
            ),
        ),
        NestedTermsAggregation(
            id="token_capitalness",
            name="Token capitalness distribution",
            description="Computes capitalization information of tokens",
            nested_path=_TOKENS_NAMESPACE,
            terms=TermsAggregation(
                id="capitalness",
                field="capitalness",
                name="",
                # missing="OTHER",
            ),
        ),
    ]
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
            description="Computes capitalization information of predicted entity mentions",
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
        MentionsByEntityDistribution(
            id="predicted_mentions_distribution",
            name="Predicted mentions distribution by entity",
            description="Computes predicted mentions distribution against its labels",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
        ),
        EntityConsistency(
            id="predicted_entity_consistency",
            name="Entity label consistency for predictions",
            description="Computes entity label variability for top-k predicted entity mentions",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            mention_field="value",
            labels_field="label",
        ),
        EntityConsistency(
            id="predicted_tag_consistency",
            name="Token tag consistency for predictions",
            description="Computes token tag variability for top-k predicted tags",
            nested_path=_PREDICTED_TAGS_NAMESPACE,
            mention_field="value",
            labels_field="tag",
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
        MentionsByEntityDistribution(
            id="annotated_mentions_distribution",
            name="Annotated mentions distribution by entity",
            description="Computes annotated mentions distribution against its labels",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
        ),
        EntityConsistency(
            id="annotated_entity_consistency",
            name="Entity label consistency for annotations",
            description="Computes entity label variability for top-k annotated entity mentions",
            nested_path=_ANNOTATED_MENTIONS_NAMESPACE,
            mention_field="value",
            labels_field="label",
        ),
        EntityConsistency(
            id="annotated_tag_consistency",
            name="Token tag consistency for annotations",
            description="Computes token tag variability for top-k annotated tags",
            nested_path=_ANNOTATED_TAGS_NAMESPACE,
            mention_field="value",
            labels_field="tag",
        ),
    ]

    metrics: ClassVar[List[BaseMetric]] = CommonTasksMetrics.metrics + [
        TermsAggregation(
            id="predicted_as",
            name="Predicted labels distribution",
            field="predicted_as",
        ),
        TermsAggregation(
            id="annotated_as",
            name="Annotated labels distribution",
            field="annotated_as",
        ),
        *_TOKENS_METRICS,
        *_PREDICTED_METRICS,
        *_ANNOTATED_METRICS,
        DatasetLabels(),
        F1Metric(
            id="F1",
            name="F1 Metric based on entity-level",
            description="F1 metrics based on entity-level (averaged and per label), "
            "where only exact matches count (CoNNL 2003).",
        ),
    ]
