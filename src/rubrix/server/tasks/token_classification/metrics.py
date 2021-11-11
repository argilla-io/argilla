from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import BaseModel, Field

from rubrix.server.commons.es_helpers import aggregations
from rubrix.server.tasks.commons.dao import extends_index_properties
from rubrix.server.tasks.commons.metrics.model.base import (
    BaseMetric,
    BaseTaskMetrics,
    ElasticsearchMetric,
    NestedPathElasticsearchMetric,
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
        return aggregations.histogram_aggregation(
            self.length_field, interval=interval or 1
        )


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


class TokenClassificationMetrics(BaseTaskMetrics):
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
                chars_length=len(mention)
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

    metrics: ClassVar[List[BaseMetric]] = [
        TokensLength(
            id="tokens_length",
            name="Tokens length",
            description="Computes the text length measured in number of tokens",
            length_field="metrics.tokens_length",
        ),
        EntityDensity(
            id="entity_density",
            name="Mention entity density",
            description="Computes the ratio between the number of all entity tokens and tokens in the text",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            density_field="density",
        ),
        EntityLabels(
            id="entity_labels",
            name="Entity labels",
            description="Entity labels distribution",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            labels_field="label",
        ),
        EntityCapitalness(
            id="entity_capitalness",
            name="Mention entity capitalness",
            description="Compute capitalization information of entity mentions",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            capitalness_field="capitalness",
        ),
        MentionLength(
            id="mention_token_length",
            name="Mention tokens length",
            description="Computes the length of the entity mention measured in number of tokens",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            length_field="tokens_length",
        ),
        MentionLength(
            id="mention_char_length",
            name="Mention characters length",
            description="Computes the length of the entity mention measured in number of tokens",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            length_field="chars_length",
        ),
        EntityConsistency(
            id="entity_consistency",
            name="Entity label consistency",
            description="Computes entity label variability for top-k entity mentions",
            nested_path=_PREDICTED_MENTIONS_NAMESPACE,
            mention_field="value",
            labels_field="label",
        ),
    ]
