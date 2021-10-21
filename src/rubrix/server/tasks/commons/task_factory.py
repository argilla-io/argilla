from typing import Any, List, Optional, Type

from pydantic import BaseModel

from rubrix.server.tasks.commons import TaskType
from rubrix.server.tasks.commons.metrics.model.base import BaseTaskMetrics


class TaskConfig(BaseModel):
    task: TaskType
    query: Any
    metrics: Optional[Type[BaseTaskMetrics]]


class TaskFactory:

    _REGISTERED_TASKS = dict()

    @classmethod
    def register_task(
        cls,
        task_type: TaskType,
        query_request: Type[Any],
        metrics: Optional[Type[BaseTaskMetrics]] = None,
    ):
        if metrics:
            metrics.configure_es_index()

        cls._REGISTERED_TASKS[task_type] = TaskConfig(
            task=task_type, query=query_request, metrics=metrics
        )

    @classmethod
    def get_all(cls) -> List[TaskConfig]:
        return [cfg for cfg in cls._REGISTERED_TASKS.values()]

    @classmethod
    def get_task_by_task_type(cls, task_type: TaskType) -> Optional[TaskConfig]:
        return cls._REGISTERED_TASKS.get(task_type)

    @classmethod
    def get_task_metrics(cls, task: TaskType) -> Optional[Type[BaseTaskMetrics]]:
        config = cls.get_task_by_task_type(task)
        if config:
            return config.metrics
