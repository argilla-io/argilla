#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import dataclasses
from typing import Any, Dict

from argilla.server.daos.backend.metrics.base import (
    BidimensionalTermsAggregation,
    HistogramAggregation,
    NestedBidimensionalTermsAggregation,
    NestedHistogramAggregation,
    NestedPathElasticsearchMetric,
    NestedTermsAggregation,
    TermsAggregation,
)
from argilla.server.daos.backend.query_helpers import aggregations

_DEFAULT_MAX_ENTITY_BUCKET = 1000


@dataclasses.dataclass
class EntityConsistency(NestedPathElasticsearchMetric):
    """Computes the entity consistency distribution"""

    mention_field: str
    labels_field: str

    def _inner_aggregation(
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


METRICS = {
    "tokens_length": HistogramAggregation(
        "tokens_length",
        field="metrics.tokens_length",
    ),
    "token_frequency": NestedTermsAggregation(
        id="token_frequency",
        nested_path="metrics.tokens",
        terms=TermsAggregation(
            id="frequency",
            field="value",
        ),
    ),
    "token_length": NestedHistogramAggregation(
        id="token_length",
        nested_path="metrics.tokens",
        histogram=HistogramAggregation(
            id="length",
            field="length",
            fixed_interval=1,
        ),
    ),
    "token_capitalness": NestedTermsAggregation(
        id="token_capitalness",
        nested_path="metrics.tokens",
        terms=TermsAggregation(
            id="capitalness",
            field="capitalness",
        ),
    ),
    "predicted_mention_char_length": NestedHistogramAggregation(
        id="predicted_mention_char_length",
        nested_path="metrics.predicted.mentions",
        histogram=HistogramAggregation(
            id="length",
            field="chars_length",
            fixed_interval=1,
        ),
    ),
    "annotated_mention_char_length": NestedHistogramAggregation(
        id="annotated_mention_char_length",
        nested_path="metrics.annotated.mentions",
        histogram=HistogramAggregation(
            id="length",
            field="chars_length",
            fixed_interval=1,
        ),
    ),
    "predicted_entity_labels": NestedTermsAggregation(
        id="predicted_entity_labels",
        nested_path="metrics.predicted.mentions",
        terms=TermsAggregation(
            id="terms",
            field="label",
            default_size=_DEFAULT_MAX_ENTITY_BUCKET,
        ),
    ),
    "annotated_entity_labels": NestedTermsAggregation(
        id="annotated_entity_labels",
        nested_path="metrics.annotated.mentions",
        terms=TermsAggregation(
            id="terms",
            field="label",
            default_size=_DEFAULT_MAX_ENTITY_BUCKET,
        ),
    ),
    "predicted_entity_density": NestedHistogramAggregation(
        id="predicted_entity_density",
        nested_path="metrics.predicted.mentions",
        histogram=HistogramAggregation(id="histogram", field="density"),
    ),
    "annotated_entity_density": NestedHistogramAggregation(
        id="annotated_entity_density",
        nested_path="metrics.annotated.mentions",
        histogram=HistogramAggregation(id="histogram", field="density"),
    ),
    "predicted_mention_token_length": NestedHistogramAggregation(
        id="predicted_mention_token_length",
        nested_path="metrics.predicted.mentions",
        histogram=HistogramAggregation(id="histogram", field="tokens_length"),
    ),
    "annotated_mention_token_length": NestedHistogramAggregation(
        id="annotated_mention_token_length",
        nested_path="metrics.annotated.mentions",
        histogram=HistogramAggregation(id="histogram", field="tokens_length"),
    ),
    "predicted_entity_capitalness": NestedTermsAggregation(
        id="predicted_entity_capitalness",
        nested_path="metrics.predicted.mentions",
        terms=TermsAggregation(id="terms", field="capitalness"),
    ),
    "annotated_entity_capitalness": NestedTermsAggregation(
        id="annotated_entity_capitalness",
        nested_path="metrics.annotated.mentions",
        terms=TermsAggregation(id="terms", field="capitalness"),
    ),
    "predicted_mentions_distribution": NestedBidimensionalTermsAggregation(
        id="predicted_mentions_distribution",
        nested_path="metrics.predicted.mentions",
        biterms=BidimensionalTermsAggregation(
            id="bi-dimensional", field_x="label", field_y="value"
        ),
    ),
    "annotated_mentions_distribution": NestedBidimensionalTermsAggregation(
        id="predicted_mentions_distribution",
        nested_path="metrics.annotated.mentions",
        biterms=BidimensionalTermsAggregation(
            id="bi-dimensional", field_x="label", field_y="value"
        ),
    ),
    "predicted_entity_consistency": EntityConsistency(
        id="predicted_entity_consistency",
        nested_path="metrics.predicted.mentions",
        mention_field="value",
        labels_field="label",
    ),
    "annotated_entity_consistency": EntityConsistency(
        id="annotated_entity_consistency",
        nested_path="metrics.annotated.mentions",
        mention_field="value",
        labels_field="label",
    ),
    "predicted_tag_consistency": EntityConsistency(
        id="predicted_tag_consistency",
        nested_path="metrics.predicted.tags",
        mention_field="value",
        labels_field="tag",
    ),
    "annotated_tag_consistency": EntityConsistency(
        id="annotated_tag_consistency",
        nested_path="metrics.annotated.tags",
        mention_field="value",
        labels_field="tag",
    ),
}
