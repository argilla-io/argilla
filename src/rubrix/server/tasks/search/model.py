from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from rubrix.server.tasks.commons import BaseRecord, SortableField, TaskStatus


class BaseSearchQuery(BaseModel):

    """
    Base search query fields

    Attributes:
    -----------
    ids: Optional[List[Union[str, int]]]
        Record ids list

    query_text: str
        Text query over inputs

    metadata: Optional[Dict[str, Union[str, List[str]]]]
        Text query over metadata fields. Default=None

    predicted_by: List[str]
        List of predicted agents

    annotated_by: List[str]
        List of annotation agents

    status: List[TaskStatus]
        List of task status

    """

    query_text: Optional[str] = None
    advanced_query_dsl: bool = False

    ids: Optional[List[Union[str, int]]]

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    status: List[TaskStatus] = Field(default_factory=list)

    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    def as_elasticsearch(self) -> Dict[str, Any]:
        # TODO: Hide transformations in DAO component
        raise NotImplementedError()


class SortConfig(BaseModel):
    shuffle: bool = False

    sort_by: List[SortableField] = Field(default_factory=list)
    valid_fields: List[str] = Field(default_factory=list)


Record = TypeVar("Record", bound=BaseRecord)


class SearchResults(BaseModel):
    total: int

    records: List[Record]
    metrics: Dict[str, Any] = Field(default_factory=dict)
