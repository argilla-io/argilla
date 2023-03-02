#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import List, Optional, Set, Type

from pydantic import BaseModel

from argilla.server.commons.models import TaskType
from argilla.server.errors import EntityNotFoundError, WrongTaskError
from argilla.server.services.datasets import ServiceBaseDataset, ServiceDataset
from argilla.server.services.metrics import ServiceBaseMetric
from argilla.server.services.metrics.models import ServiceBaseTaskMetrics
from argilla.server.services.search.model import ServiceRecordsQuery
from argilla.server.services.tasks.commons import ServiceRecord


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
        query_request: Type[ServiceRecordsQuery],
        record_class: Type[ServiceRecord],
        dataset_class: Optional[Type[ServiceDataset]] = None,
        metrics: Optional[Type[ServiceBaseTaskMetrics]] = None,
    ):
        cls.__REGISTERED_TASKS__[task_type] = TaskConfig(
            task=task_type,
            dataset=dataset_class or ServiceBaseDataset,
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
    def find_task_metric(cls, task: TaskType, metric_id: str) -> Optional[ServiceBaseMetric]:
        metrics = cls.find_task_metrics(task, {metric_id})
        if metrics:
            return metrics[0]
        raise EntityNotFoundError(name=metric_id, type=ServiceBaseMetric)

    @classmethod
    def find_task_metrics(cls, task: TaskType, metric_ids: Set[str]) -> List[ServiceBaseMetric]:
        if not metric_ids:
            return []

        metrics = []
        for metric in cls.get_task_metrics(task).metrics:
            if metric.id in metric_ids:
                metrics.append(metric)
        return metrics
