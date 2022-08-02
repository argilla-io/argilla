from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from rubrix.server.services.tasks.commons.record import Record, TaskStatus


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class SortableField(BaseModel):
    """Sortable field structure"""

    id: str
    order: SortOrder = SortOrder.asc


class BaseSearchQuery(BaseModel):

    query_text: Optional[str] = None
    advanced_query_dsl: bool = False

    ids: Optional[List[Union[str, int]]]

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    status: List[TaskStatus] = Field(default_factory=list)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None
    last_record_identifier: Optional[str] = None


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
