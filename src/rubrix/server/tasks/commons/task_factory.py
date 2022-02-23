from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from rubrix.server.commons.errors import WrongTaskError
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.tasks.commons import BaseRecord, TaskType
from rubrix.server.tasks.commons.metrics.model.base import BaseTaskMetrics


class TaskConfig(BaseModel):
    task: TaskType
    query: Any
    dataset: Type[DatasetDB]
    record: Type[BaseRecord]
    metrics: Optional[Type[BaseTaskMetrics]]
    es_mappings: Dict[str, Any]


class TaskFactory:

    _REGISTERED_TASKS = dict()

    @classmethod
    def register_task(
        cls,
        task_type: TaskType,
        dataset_class: Type[DatasetDB],
        query_request: Type[Any],
        es_mappings: Dict[str, Any],
        record_class: Type[BaseRecord],
        metrics: Optional[Type[BaseTaskMetrics]] = None,
    ):
        cls._REGISTERED_TASKS[task_type] = TaskConfig(
            task=task_type,
            dataset=dataset_class,
            es_mappings=es_mappings,
            query=query_request,
            record=record_class,
            metrics=metrics,
        )

    @classmethod
    def get_all_configs(cls) -> List[TaskConfig]:
        return [cfg for cfg in cls._REGISTERED_TASKS.values()]

    @classmethod
    def get_task_by_task_type(cls, task_type: TaskType) -> Optional[TaskConfig]:
        return cls._REGISTERED_TASKS.get(task_type)

    @classmethod
    def get_task_metrics(cls, task: TaskType) -> Optional[Type[BaseTaskMetrics]]:
        config = cls.get_task_by_task_type(task)
        if config:
            return config.metrics

    @classmethod
    def get_task_dataset(cls, task: TaskType) -> Type[DatasetDB]:
        config = cls.__get_task_config__(task)
        return config.dataset

    @classmethod
    def get_task_record(cls, task: TaskType) -> Type[BaseRecord]:
        config = cls.__get_task_config__(task)
        return config.record

    @classmethod
    def get_task_mappings(cls, task: TaskType) -> Dict[str, Any]:
        config = cls.__get_task_config__(task)
        return config.es_mappings

    @classmethod
    def __get_task_config__(cls, task):
        config = cls.get_task_by_task_type(task)
        if not config:
            raise WrongTaskError(f"No configuration found for task {task}")
        return config
