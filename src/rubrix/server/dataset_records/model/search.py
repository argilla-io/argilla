from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, PrivateAttr
from rubrix.logging import LoggingMixin
from rubrix.server.commons.models import (
    PredictionStatus,
    RecordTaskInfo,
    TaskStatus,
    TaskType,
)
from rubrix.server.dataset_records.es_helpers import aggregations, filters


class DefaultTaskSearchFilters(BaseModel):
    """
    Query filters to apply by task

    Attributes:
    -----------

    predicted_as: List[str]
        List of predicted terms
    annotated_as: List[str]
        List of annotated terms

    annotated_by: List[str]
        List of annotation agents
    predicted_by: List[str]
        List of predicted agents

    status: List[TaskStatus]
        List of task status
    predicted: Optional[PredictionStatus]
        The task prediction status

    """

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    status: List[TaskStatus] = Field(default_factory=list)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)

    def as_elasticsearch(self) -> List[Dict[str, Any]]:
        """Convert filter configuration as a list of elasticsearch filters"""
        return [
            query_filter
            for query_filter in [
                filters.predicted_as(self.predicted_as),
                filters.predicted_by(self.predicted_by),
                filters.annotated_as(self.annotated_as),
                filters.annotated_by(self.annotated_by),
                filters.status(self.status),
                filters.predicted(self.predicted),
            ]
            if query_filter
        ]


class BaseTaskSearchAggregations(BaseModel):
    """
    Search aggregation result for task

    Attributes:
    -----------

    predicted_as: Dict[str, int]
        Occurrence info about more relevant predicted terms
    annotated_as: Dict[str, int]
        Occurrence info about more relevant annotated terms

    annotated_by: Dict[str, int]
        Occurrence info about more relevant annotation agent terms
    predicted_by: Dict[str, int]
        Occurrence info about more relevant prediction agent terms

    status: Dict[str, int]
        Occurrence info about task status
    predicted: Dict[str, int]
        Occurrence info about task prediction status

    """

    predicted_as: Dict[str, int] = Field(default_factory=dict)
    annotated_as: Dict[str, int] = Field(default_factory=dict)

    annotated_by: Dict[str, int] = Field(default_factory=dict)
    predicted_by: Dict[str, int] = Field(default_factory=dict)

    status: Dict[str, int] = Field(default_factory=dict)
    predicted: Dict[str, int] = Field(default_factory=dict)

    @classmethod
    def elasticsearch_aggregations(cls) -> Dict[str, Any]:
        """Prepare elasticsearch aggregation search section with common aggregations """

        return {
            **aggregations.predicted_as(),
            **aggregations.predicted_by(),
            **aggregations.annotated_as(),
            **aggregations.annotated_by(),
            **aggregations.status(),
            **aggregations.predicted(),
        }


class TaskMeta(BaseModel, LoggingMixin):
    """
    Task meta information data model

    Attributes:
    -----------

    task_info: Type[RecordTaskInfo]
        The task record data model
    filters: DefaultTaskSearchFilters
        The query filters to apply in search
    aggregations: Type[BaseTaskSearchAggregations]
        The search aggregation results data model. Default=BaseTaskSearchAggregations

    """

    task_info: Type[RecordTaskInfo]
    filters: DefaultTaskSearchFilters
    aggregations: Type[BaseTaskSearchAggregations] = BaseTaskSearchAggregations

    @property
    def task(self) -> TaskType:
        """The task type"""
        return self.task_info.task()


class RecordSearchAggregations(BaseModel, LoggingMixin):
    """
    Records search result aggregations

    Attributes:
    -----------

    words_cloud: Dict[str,int]
        Word cloud aggregations

    metadata_aggregations: Dict[str, Dict[str, int]]
        Metadata fields aggregations

    """

    words_cloud: Dict[str, int] = Field(default_factory=dict)
    metadata_aggregations: Dict[str, Dict[str, int]] = Field(default_factory=dict)

    __tasks__: Dict[TaskType, BaseTaskSearchAggregations] = PrivateAttr(
        default_factory=dict
    )

    def task_aggregations(self, task: TaskType) -> Optional[BaseTaskSearchAggregations]:
        """
        Get the resulting search aggregation for task

        Parameters
        ----------
        task:
            The task type

        Returns
        -------
            Result aggregations task if found. None otherwise

        """
        return self.__tasks__.get(task)

    def set_task_aggregations(
        self, task: TaskType, aggregations: BaseTaskSearchAggregations
    ):
        """
        Set the task results aggregations

        Parameters
        ----------
        task:
            The task type
        aggregations:
            The task query result aggregations

        """
        if task is None:
            raise ValueError("Missing task type")

        if aggregations is None:
            raise ValueError("Missing task filters")

        if task in self.__tasks__:
            self.logger.warning(
                "Aggregations already defined for task {}. It will be overrides",
                task,
            )
        self.__tasks__[task] = aggregations
