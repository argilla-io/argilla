from typing import Any, Dict, List, TypeVar

from pydantic import BaseModel, Field

from rubrix.server.daos.backend.search.model import (
    BaseRecordsQuery,
    QueryRange,
    SortableField,
    SortConfig,
)
from rubrix.server.services.tasks.commons import ServiceRecord


class ServiceBaseRecordsQuery(BaseRecordsQuery):
    pass


class ServiceSortConfig(SortConfig):
    pass


class ServiceSortableField(SortableField):
    """Sortable field structure"""

    pass


class ServiceQueryRange(QueryRange):
    pass


class ServiceScoreRange(ServiceQueryRange):
    pass


class ServiceBaseSearchResultsAggregations(BaseModel):

    predicted_as: Dict[str, int] = Field(default_factory=dict)
    annotated_as: Dict[str, int] = Field(default_factory=dict)
    annotated_by: Dict[str, int] = Field(default_factory=dict)
    predicted_by: Dict[str, int] = Field(default_factory=dict)
    status: Dict[str, int] = Field(default_factory=dict)
    predicted: Dict[str, int] = Field(default_factory=dict)
    score: Dict[str, int] = Field(default_factory=dict)
    words: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


ServiceSearchResultsAggregations = TypeVar(
    "ServiceSearchResultsAggregations", bound=ServiceBaseSearchResultsAggregations
)


class ServiceSearchResults(BaseModel):
    total: int
    records: List[ServiceRecord]
    metrics: Dict[str, Any] = Field(default_factory=dict)


ServiceRecordsQuery = TypeVar("ServiceRecordsQuery", bound=ServiceBaseRecordsQuery)
