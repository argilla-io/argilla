from enum import Enum
from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from rubrix.server.elasticseach.search.model import BaseSearchQuery as _BaseSearchQuery
from rubrix.server.elasticseach.search.model import SortableField as _SortableField
from rubrix.server.elasticseach.search.model import SortOrder
from rubrix.server.services.tasks.commons.record import Record


class BaseSVCSearchQuery(_BaseSearchQuery):
    pass


class SortableField(_SortableField):
    """Sortable field structure"""

    pass


class QueryRange(BaseModel):

    range_from: float = Field(default=0.0, alias="from")
    range_to: float = Field(default=None, alias="to")

    class Config:
        allow_population_by_field_name = True


class SortConfig(BaseModel):
    shuffle: bool = False

    sort_by: List[SortableField] = Field(default_factory=list)
    valid_fields: List[str] = Field(default_factory=list)


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


class BaseSearchResults(GenericModel, Generic[Record, Aggregations]):
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
    records: List[Record] = Field(default_factory=list)
    aggregations: Aggregations = None


class SearchResults(BaseModel):
    total: int
    records: List[Record]
    metrics: Dict[str, Any] = Field(default_factory=dict)
