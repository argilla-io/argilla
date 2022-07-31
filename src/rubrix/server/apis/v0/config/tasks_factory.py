from typing import Any, List, Optional, Set, Type

from pydantic import BaseModel

from rubrix.server.apis.v0.models.commons.model import TaskType
from rubrix.server.apis.v0.models.datasets import BaseDatasetDB
from rubrix.server.apis.v0.models.metrics.base import BaseTaskMetrics, Metric
from rubrix.server.apis.v0.models.metrics.text_classification import (
    TextClassificationMetrics,
)
from rubrix.server.apis.v0.models.metrics.token_classification import (
    TokenClassificationMetrics,
)
from rubrix.server.apis.v0.models.text2text import (
    Text2TextDatasetDB,
    Text2TextMetrics,
    Text2TextQuery,
    Text2TextRecord,
)
from rubrix.server.apis.v0.models.text_classification import (
    TextClassificationDatasetDB,
    TextClassificationQuery,
    TextClassificationRecord,
)
from rubrix.server.apis.v0.models.token_classification import (
    TokenClassificationDatasetDB,
    TokenClassificationQuery,
    TokenClassificationRecord,
)
from rubrix.server.errors import EntityNotFoundError, WrongTaskError
from rubrix.server.services.datasets import ServiceDataset
from rubrix.server.services.tasks.commons import ServiceBaseRecord


class TaskConfig(BaseModel):
    task: TaskType
    query: Any
    dataset: Type[ServiceDataset]
    record: Type[ServiceBaseRecord]
    metrics: Optional[Type[BaseTaskMetrics]]


class TaskFactory:

    _REGISTERED_TASKS = dict()

    @classmethod
    def register_task(
        cls,
        task_type: TaskType,
        dataset_class: Type[ServiceDataset],
        query_request: Type[Any],
        record_class: Type[ServiceBaseRecord],
        metrics: Optional[Type[BaseTaskMetrics]] = None,
    ):
        cls._REGISTERED_TASKS[task_type] = TaskConfig(
            task=task_type,
            dataset=dataset_class,
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
    def get_task_dataset(cls, task: TaskType) -> Type[BaseDatasetDB]:
        config = cls.__get_task_config__(task)
        return config.dataset

    @classmethod
    def get_task_record(cls, task: TaskType) -> Type[ServiceBaseRecord]:
        config = cls.__get_task_config__(task)
        return config.record

    @classmethod
    def __get_task_config__(cls, task):
        config = cls.get_task_by_task_type(task)
        if not config:
            raise WrongTaskError(f"No configuration found for task {task}")
        return config

    @classmethod
    def find_task_metric(cls, task: TaskType, metric_id: str) -> Optional[Metric]:
        metrics = cls.find_task_metrics(task, {metric_id})
        if metrics:
            return metrics[0]
        raise EntityNotFoundError(name=metric_id, type=Metric)

    @classmethod
    def find_task_metrics(cls, task: TaskType, metric_ids: Set[str]) -> List[Metric]:

        if not metric_ids:
            return []

        metrics = []
        for metric in cls.get_task_metrics(task).metrics:
            if metric.id in metric_ids:
                metrics.append(metric)
        return metrics


TaskFactory.register_task(
    task_type=TaskType.token_classification,
    dataset_class=TokenClassificationDatasetDB,
    query_request=TokenClassificationQuery,
    record_class=TokenClassificationRecord,
    metrics=TokenClassificationMetrics,
)

TaskFactory.register_task(
    task_type=TaskType.text_classification,
    dataset_class=TextClassificationDatasetDB,
    query_request=TextClassificationQuery,
    record_class=TextClassificationRecord,
    metrics=TextClassificationMetrics,
)

TaskFactory.register_task(
    task_type=TaskType.text2text,
    dataset_class=Text2TextDatasetDB,
    query_request=Text2TextQuery,
    record_class=Text2TextRecord,
    metrics=Text2TextMetrics,
)
