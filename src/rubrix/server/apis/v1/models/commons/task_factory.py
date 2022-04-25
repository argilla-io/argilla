from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from rubrix.server.apis.v1.models.commons.task import TaskType
from rubrix.server.apis.v1.models.dataset_settings import AbstractDatasetSettings
from rubrix.server.apis.v1.models.datasets import (
    AbstractBaseDataset,
    Dataset,
    DatasetCreate,
    DatasetUpdate,
)


@dataclass
class TaskFactory:

    task: TaskType

    es_mapping: Dict[str, Any]

    # Datasets
    create_dataset_class: Type[DatasetCreate] = DatasetCreate
    update_dataset_class: Type[DatasetUpdate] = DatasetUpdate
    output_dataset_class: Type[AbstractBaseDataset] = Dataset

    # Settings
    settings_class: Optional[Type[AbstractDatasetSettings]] = None
