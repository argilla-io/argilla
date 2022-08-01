from typing import List, Optional, Set, Type

from pydantic import BaseModel

from rubrix.server.commons.models import TaskType
from rubrix.server.errors import EntityNotFoundError, WrongTaskError
from rubrix.server.services.datasets import ServiceDataset
from rubrix.server.services.metrics import ServiceBaseMetric
from rubrix.server.services.metrics.models import ServiceBaseTaskMetrics
from rubrix.server.services.search.model import ServiceRecordsQuery
from rubrix.server.services.tasks.commons import ServiceRecord


class TaskConfig(BaseModel):
    task: TaskType
    query: Type[ServiceRecordsQuery]
    dataset: Type[ServiceDataset]
    record: Type[ServiceRecord]
    metrics: Optional[Type[ServiceBaseTaskMetrics]]


class TasksFactory:

    __REGISTERED_TASKS__ = dict()

    @classmethod
    def register_task(
        cls,
        task_type: TaskType,
        dataset_class: Type[ServiceDataset],
        query_request: Type[ServiceRecordsQuery],
        record_class: Type[ServiceRecord],
        metrics: Optional[Type[ServiceBaseTaskMetrics]] = None,
    ):

        cls.__REGISTERED_TASKS__[task_type] = TaskConfig(
            task=task_type,
            dataset=dataset_class,
            query=query_request,
            record=record_class,
            metrics=metrics,
        )

    @classmethod
    def get_all_configs(cls) -> List[TaskConfig]:
        return [cfg for cfg in cls.__REGISTERED_TASKS__.values()]

    @classmethod
    def get_task_by_task_type(cls, task_type: TaskType) -> Optional[TaskConfig]:
        return cls.__REGISTERED_TASKS__.get(task_type)

    @classmethod
    def get_task_metrics(cls, task: TaskType) -> Optional[Type[ServiceBaseTaskMetrics]]:
        config = cls.get_task_by_task_type(task)
        if config:
            return config.metrics

    @classmethod
    def get_task_dataset(cls, task: TaskType) -> Type[ServiceDataset]:
        config = cls.__get_task_config__(task)
        return config.dataset

    @classmethod
    def get_task_record(cls, task: TaskType) -> Type[ServiceRecord]:
        config = cls.__get_task_config__(task)
        return config.record

    @classmethod
    def __get_task_config__(cls, task):
        config = cls.get_task_by_task_type(task)
        if not config:
            raise WrongTaskError(f"No configuration found for task {task}")
        return config

    @classmethod
    def find_task_metric(
        cls, task: TaskType, metric_id: str
    ) -> Optional[ServiceBaseMetric]:
        metrics = cls.find_task_metrics(task, {metric_id})
        if metrics:
            return metrics[0]
        raise EntityNotFoundError(name=metric_id, type=ServiceBaseMetric)

    @classmethod
    def find_task_metrics(
        cls, task: TaskType, metric_ids: Set[str]
    ) -> List[ServiceBaseMetric]:

        if not metric_ids:
            return []

        metrics = []
        for metric in cls.get_task_metrics(task).metrics:
            if metric.id in metric_ids:
                metrics.append(metric)
        return metrics
