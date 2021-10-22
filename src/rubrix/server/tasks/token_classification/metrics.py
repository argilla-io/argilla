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


class SentenceLength(ElasticsearchMetric):
    """
    Summarizes the sentence length metric into an histogram

    Attributes:
    -----------
    length_field:
        The elasticsearch field where sentence length is stored
    """

    length_field: str

    def aggregation_request(self, interval: int) -> Dict[str, Any]:
        return aggregations.histogram_aggregation(self.length_field, interval=interval)


class EntityTags(NestedPathElasticsearchMetric):
    """
    Calculates the entity tags distribution

    Attributes:
    -----------
    tags_field:
        The elasticsearch field where tags are stored
    """

    tags_field: str

    def inner_aggregation(self, size: int = 10) -> Dict[str, Any]:
        return {"tags": aggregations.terms_aggregation(self.tags_field, size=size)}


class EntityDensity(NestedPathElasticsearchMetric):
    """Summarizes the entity density metric into an histogram"""

    density_field: str

    def inner_aggregation(self, interval: float = 0.1) -> Dict[str, Any]:
        return {
            "density": aggregations.histogram_aggregation(
                field_name=self.density_field, interval=interval
            )
        }


class MentionLength(NestedPathElasticsearchMetric):
    """Summarizes the mention length into an histogram"""

    length_field: str

    def inner_aggregation(self, interval: int = 1) -> Dict[str, Any]:
        return {
            "mention_length": aggregations.histogram_aggregation(
                self.length_field, interval=interval
            )
        }


class EntityCapitalness(NestedPathElasticsearchMetric):
    """Calculates the mention capitalness distribution"""

    capitalness_field: str

    def inner_aggregation(self) -> Dict[str, Any]:
        return {
            "capitalness": aggregations.terms_aggregation(
                self.capitalness_field, size=4  # The number of capitalness choices
            )
        }


class MentionConsistency(NestedPathElasticsearchMetric):
    """Calculates the mention consistence distribution"""

    mention_field: str
    entity_field: str

    def inner_aggregation(
        self,
        size: int = 20,
        entity_size: int = 10,
    ) -> Dict[str, Any]:
        return {
            "consistency": {
                **aggregations.terms_aggregation(self.mention_field, size=size),
                "aggs": {
                    "entities": aggregations.terms_aggregation(
                        self.entity_field, size=entity_size
                    ),
                    "count": {"cardinality": {"field": self.entity_field}},
                    "sortby_entities_count": {
                        "bucket_sort": {
                            "sort": [{"count": {"order": "desc"}}],
                            "size": entity_size,
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
                    {"entity": entity, "count": count}
                    for entity, count in mention_aggs["entities"].items()
                ],
            }
            for mention, mention_aggs in aggregation_result.items()
        ]
        result.sort(key=lambda m: len(m["entities"]), reverse=True)
        return { "metions": result }


class TokenClassificationMetrics(BaseTaskMetrics):
    """Configured metrics for token classification"""

    class MentionMetrics(BaseModel):
        """Mention metrics model"""

        mention: str
        entity: str
        score: float = Field(ge=0.0)
        capitalness: str = Field(...)
        density: float = Field(ge=0.0)
        length: int = Field(g=0)

    @staticmethod
    def mentions_metrics(
        mentions: List[Tuple[str, EntitySpan]],
        tokens: List[str],
        chars2tokens: Dict[int, int],
    ) -> List[MentionMetrics]:
        """Given a list of mentions with its entity spans, calculate all required metrics"""

        def mention_capitalness(mention: str) -> str:
            """Calculate mention capitalness"""
            mention = mention.strip()
            if mention.upper() == mention:
                return "UPPER"
            if mention.lower() == mention:
                return "LOWER"
            if mention[0].isupper():
                return "FIRST"
            return "MIDDLE"

        def mention_length(entity: EntitySpan, chars2token_map: Dict[int, int]) -> int:
            """Calculate mention tokens length"""
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

        def mention_density(mention_length: int, sentence_length: int) -> float:
            """Calculate mention density"""
            return (1.0 * mention_length) / sentence_length

        return [
            TokenClassificationMetrics.MentionMetrics(
                mention=mention,
                entity=entity.label,
                score=entity.score,
                capitalness=mention_capitalness(mention),
                density=mention_density(_mention_length, sentence_length=len(tokens)),
                length=_mention_length,
            )
            for mention, entity in mentions
            for _mention_length in [
                mention_length(entity, chars2tokens),
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
                relative_idx >= len(record.tokens[current_token])
                and char == record.tokens[current_token + 1][0]
            ):
                current_token += 1
                current_token_char_start += relative_idx
                chars_map[idx] = current_token
        return chars_map

    @classmethod
    def configure_es_index(cls):
        """Configure mentions as nested properties"""
        mentions_configuration = {
            "type": "nested",
            "properties": {
                "mention": {"type": "keyword"},
                "entity": {"type": "keyword"},
                "score": {"type": "float"},
                "capitalness": {"type": "keyword"},
                "density": {"type": "float"},
                "length": {"type": "integer"},
            },
        }
        extends_index_properties(
            {
                "metrics.mentions.predicted": mentions_configuration,
                "metrics.mentions.annotated": mentions_configuration,
            }
        )

    @classmethod
    def record_metrics(cls, record: TokenClassificationRecord) -> Dict[str, Any]:
        """Calculate metrics at record level"""
        chars2tokens = cls.build_chars2tokens_map(record)

        return {
            "sentence_length": len(record.tokens),
            "mentions.predicted": cls.mentions_metrics(
                mentions=record.predicted_mentions(),
                tokens=record.tokens,
                chars2tokens=chars2tokens,
            ),
            "mentions.annotated": cls.mentions_metrics(
                mentions=record.annotated_mentions(),
                tokens=record.tokens,
                chars2tokens=chars2tokens,
            ),
        }

    metrics: ClassVar[List[BaseMetric]] = [
        SentenceLength(
            id="sentence_length",
            name="Sentence tokens length",
            description="Calculates tokens length",
            length_field="metrics.sentence_length",
        ),
        EntityDensity(
            id="entity_density",
            name="Mention entity density",
            description="Calculates relation between mention tokens and sentence tokens",
            nested_path="metrics.mentions.predicted",
            density_field="metrics.mentions.predicted.density",
        ),
        EntityTags(
            id="entity_tags",
            name="Entity tags",
            description="The entity tags distribution",
            nested_path="metrics.mentions.predicted",
            tags_field="metrics.mentions.predicted.entity",
        ),
        EntityCapitalness(
            id="entity_capitalness",
            name="Mention entity capitalness",
            description="Calculate capitalized information for mentions",
            nested_path="metrics.mentions.predicted",
            capitalness_field="metrics.mentions.predicted.capitalness",
        ),
        MentionLength(
            id="mention_length",
            name="Mention length",
            description="The token level mention length",
            nested_path="metrics.mentions.predicted",
            length_field="metrics.mentions.predicted.length",
        ),
        MentionConsistency(
            id="mention_consistency",
            name="Mention entity consistency",
            description="Calculates top k-mentions with more entity variability",
            nested_path="metrics.mentions.predicted",
            mention_field="metrics.mentions.predicted.mention",
            entity_field="metrics.mentions.predicted.entity",
        ),
    ]
