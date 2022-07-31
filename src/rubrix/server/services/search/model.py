from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from rubrix.server.backend.search.model import BaseRecordsQuery as _BaseSearchQuery
from rubrix.server.backend.search.model import QueryRange as _QueryRange
from rubrix.server.backend.search.model import SortableField as _SortableField
from rubrix.server.backend.search.model import SortConfig as _SortConfig
from rubrix.server.services.tasks.commons.record import ServiceRecord


class BaseSearchQuery(_BaseSearchQuery):
    pass


ServiceSearchQuery = TypeVar("ServiceSearchQuery", bound=BaseSearchQuery)


class SortConfig(_SortConfig):
    pass


class SortableField(_SortableField):
    """Sortable field structure"""

    pass


class QueryRange(_QueryRange):
    pass


class ScoreRange(QueryRange):
    pass


class BaseSearchResultsAggregations(BaseModel):

    predicted_as: Dict[str, int] = Field(default_factory=dict)
    annotated_as: Dict[str, int] = Field(default_factory=dict)
    annotated_by: Dict[str, int] = Field(default_factory=dict)
    predicted_by: Dict[str, int] = Field(default_factory=dict)
    status: Dict[str, int] = Field(default_factory=dict)
    predicted: Dict[str, int] = Field(default_factory=dict)
    score: Dict[str, int] = Field(default_factory=dict)
    words: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


Aggregations = TypeVar("Aggregations", bound=BaseSearchResultsAggregations)


class BaseSearchResults(GenericModel, Generic[ServiceRecord, Aggregations]):
    """
    API search results

    Attributes:
    -----------

    total:
        The total number of records
    records:
        The selected records to return
    aggregations:
        Requested aggregations
    """

    total: int = 0
    records: List[ServiceRecord] = Field(default_factory=list)
    aggregations: Aggregations = None


class SearchResults(BaseModel):
    total: int
    records: List[ServiceRecord]
    metrics: Dict[str, Any] = Field(default_factory=dict)
