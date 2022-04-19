from dataclasses import dataclass
from typing import Optional, Type

from rubrix.server.api.v1.models.commons.task import TaskType
from rubrix.server.api.v1.models.datasets import (
    AbstractBaseDataset,
    DatasetCreate,
    DatasetUpdate,
)
from rubrix.server.api.v1.models.weak_supervision import _Rule, _RuleCreate, _RuleUpdate
from rubrix.server.tasks.commons import BaseRecord
from rubrix.server.tasks.commons.service import TaskService
from rubrix.server.tasks.search.model import BaseSearchQuery


@dataclass
class TaskFactory:

    task: TaskType
    # Common
    service_class: Type[TaskService]
    # Datasets
    create_dataset_class: Type[DatasetCreate]
    update_dataset_class: Type[DatasetUpdate]
    output_dataset_class: Type[AbstractBaseDataset]
    # Logging and search (Could be split)
    record_class: Type[BaseRecord]
    # Search
    query_class: Type[BaseSearchQuery]
    # Weak Supervision
    create_rule_class: Optional[Type[_RuleCreate]] = None
    update_rule_class: Optional[Type[_RuleUpdate]] = None
    output_rule_class: Optional[Type[_Rule]] = None
