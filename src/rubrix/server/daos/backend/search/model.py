from enum import Enum
from typing import Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from rubrix.server.commons.models import TaskStatus


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class QueryRange(BaseModel):

    range_from: float = Field(default=0.0, alias="from")
    range_to: float = Field(default=None, alias="to")

    class Config:
        allow_population_by_field_name = True


class SortableField(BaseModel):
    """Sortable field structure"""

    id: str
    order: SortOrder = SortOrder.asc


class SortConfig(BaseModel):
    shuffle: bool = False

    sort_by: List[SortableField] = Field(default_factory=list)
    valid_fields: List[str] = Field(default_factory=list)


class BaseQuery(BaseModel):
    pass


class BaseDatasetsQuery(BaseQuery):
    tasks: Optional[List[str]] = None
    owners: Optional[List[str]] = None
    include_no_owner: bool = None


class BaseRecordsQuery(BaseQuery):

    query_text: Optional[str] = None
    advanced_query_dsl: bool = False

    ids: Optional[List[Union[str, int]]]

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    status: List[TaskStatus] = Field(default_factory=list)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    has_annotation: Optional[bool] = None
    has_prediction: Optional[bool] = None


BackendQuery = TypeVar("BackendQuery", bound=BaseQuery)
BackendRecordsQuery = TypeVar("BackendRecordsQuery", bound=BaseRecordsQuery)
BackendDatasetsQuery = TypeVar("BackendDatasetsQuery", bound=BaseDatasetsQuery)
