from typing import Dict, List, Optional, Union

from pydantic import BaseModel, PrivateAttr
from rubrix.logging import LoggingMixin
from rubrix.server.commons.models import Field, SortOrder, TaskType

from .record import MultiTaskRecord
from .search import RecordSearchAggregations, TaskMeta


class AddRecordsResponse(BaseModel):
    """
    Response for records bulk

    Attributes:
    -----------
    processed: int
        Number of processed bulk records

    failed: int
        Number of failed bulk records
    """

    processed: int = 0
    failed: int = 0


class MultiTaskSortParam(BaseModel):
    """
    Sort param including task type

    Attributes:
    -----------
    by: str
        The by sort param
    order: SortOrder
        The sort order
    task: Optional[TaskType] = None
        The sort task context

    """

    by: str
    order: SortOrder
    task: Optional[TaskType] = None


class MultiTaskRecordSearchQuery(BaseModel, LoggingMixin):
    """
    Records search query model

    Attributes:
    -----------

    text_query: Optional[Union[str, Dict[str, str]]]
        The elasticsearch text query
    metadata: Dict[str, Union[str, List[str]]]
        The elasticsearch metadata query

    """

    text_query: Optional[Union[str, Dict[str, str]]] = None
    metadata: Dict[str, Union[str, List[str]]] = Field(default=dict)

    __tasks__: Dict[TaskType, TaskMeta] = PrivateAttr(default_factory=dict)

    @property
    def tasks(self) -> List[TaskType]:
        """The configured task types"""
        return list(self.__tasks__.keys())

    def task_meta(self, task: TaskType) -> Optional[TaskMeta]:
        """
        Get the configured task meta for search query

        Parameters
        ----------

        task:
            The task type

        Returns
        -------
            Configured task if found. None otherwise

        """
        return self.__tasks__.get(task)

    def with_task(self, meta: TaskMeta):
        """
        Set the task query meta

        Parameters
        ----------
        meta:
            The task

        Returns
        -------
            The self instance

        """
        if meta is None:
            raise ValueError("Missing task info")

        if meta.task in self.__tasks__:
            self.logger.warning(
                "Task {} already defined. It will be overrides",
                meta,
            )
        self.__tasks__[meta.task] = meta

        return self


class MultitaskRecordSearchResults(BaseModel):
    """
    Records search results model

    Attributes:
    -----------

    total: int
        Number of total records
    records: List[MultiTaskRecord]
        The fetched record list
    aggregations: Optional[RecordSearchAggregations]
        The query result aggregations

    """

    total: int = 0
    records: List[MultiTaskRecord]
    aggregations: RecordSearchAggregations
