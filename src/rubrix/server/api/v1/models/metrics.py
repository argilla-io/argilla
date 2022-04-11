import dataclasses
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field

from rubrix.server.api.v1.models.commons.params import build_pagination_params


class MetricInfo(BaseModel):
    id: str = Field(description="The metric id")
    name: str = Field(description="The metric name")
    description: Optional[str] = Field(
        default=None, description="The metric description"
    )


class DatasetMetrics(BaseModel):
    total: int = Field(description="Total number of metrics available for datadaset")
    metrics: List[MetricInfo]


@dataclasses.dataclass
class MetricSummaryParams:
    interval: Optional[float] = Query(
        default=None,
        gt=0.0,
        description="The histogram interval for histogram summaries",
    )
    size: Optional[int] = Query(
        default=None,
        ge=1,
        description="The number of terms for terminological summaries",
    )


PaginationParams = build_pagination_params(item_type="metric")
