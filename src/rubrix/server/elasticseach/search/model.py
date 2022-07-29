from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from rubrix.server.commons.models import TaskStatus


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class SortableField(BaseModel):
    """Sortable field structure"""

    id: str
    order: SortOrder = SortOrder.asc


class AbstractQuery(BaseModel):
    pass


class DatasetsQuery(AbstractQuery):
    tasks: Optional[List[str]] = None
    owners: Optional[List[str]] = None
    include_no_owner: bool = None


class BaseSearchQuery(AbstractQuery):

    query_text: Optional[str] = None
    advanced_query_dsl: bool = False

    ids: Optional[List[Union[str, int]]]

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    status: List[TaskStatus] = Field(default_factory=list)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    has_annotation: Optional[bool] = None
    has_prediction: Optional[bool] = None
