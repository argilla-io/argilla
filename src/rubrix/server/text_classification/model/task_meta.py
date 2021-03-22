import math
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from rubrix.server.dataset_records.model import (
    BaseTaskSearchAggregations,
    DefaultTaskSearchFilters,
)


class TaskSearchAggregations(BaseTaskSearchAggregations):
    """Aggregation results for text classification"""

    confidence: Dict[str, int] = Field(default_factory=dict)

    @classmethod
    def elasticsearch_aggregations(cls) -> Dict[str, Any]:
        return {**super().elasticsearch_aggregations(), **es_confidence_aggregation()}


class ConfidenceRange(BaseModel):
    """Confidence range filter"""

    range_from: float = Field(default=0.0, alias="from")
    range_to: float = Field(default=1.0, alias="to")

    class Config:
        allow_population_by_field_name = True


class TaskSearchFilters(DefaultTaskSearchFilters):
    """Extended filters for text classification"""

    confidence: Optional[ConfidenceRange] = None

    def as_elasticsearch(self) -> List[Dict[str, Any]]:
        filters = super().as_elasticsearch()
        confidence_filter = self.elasticsearch_confidence()
        if confidence_filter:
            filters.append(confidence_filter)
        return filters

    def elasticsearch_confidence(self) -> Optional[Dict[str, Any]]:
        if self.confidence is None:
            return None
        return {
            "range": {
                "confidences": {
                    "gte": self.confidence.range_from,
                    "lte": self.confidence.range_to,
                }
            }
        }


def es_confidence_aggregation(
    range_from: float = 0.0, range_to: float = 1.0, interval: float = 0.05
):
    decimals = 0
    _interval = interval
    while _interval < 1:
        _interval *= 10
        decimals += 1

    ten_decimals = math.pow(10, decimals)

    int_from = math.floor(range_from * ten_decimals)
    int_to = math.floor(range_to * ten_decimals)
    int_interval = math.floor(interval * ten_decimals)

    return {
        "confidence": {
            "range": {
                "field": "confidences",
                "ranges": [
                    {"from": _from / ten_decimals, "to": _to / ten_decimals}
                    for _from, _to in zip(
                        range(int_from, int_to, int_interval),
                        range(
                            int_from + int_interval, int_to + int_interval, int_interval
                        ),
                    )
                ]
                + [{"from": range_to}],
            }
        }
    }
