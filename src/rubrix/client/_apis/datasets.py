from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from rubrix.client._apis.base import AbstractApi, api_compatibility_check
from rubrix.client.sdk.datasets.api import get_dataset
from rubrix.client.sdk.datasets.models import TaskType


class Dataset(BaseModel):
    name: str
    task: TaskType
    owner: str = None
    created_at: datetime = None
    last_updated: datetime = None

    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Settings(BaseModel):
    labels_schema: Dict[str, Any]


class Datasets(AbstractApi):
    @api_compatibility_check
    def create(self, name: str, task: TaskType, settings: Optional[Settings] = None):
        dataset = Dataset(name=name, task=task)
        self.__client__.post(f"api/v1/{task}", json=dataset.dict())
        if settings is not None:
            self.save_settings(dataset, settings=settings)

    def find_by_name(self, name: str) -> Dataset:
        dataset = get_dataset(self.__client__, name=name).parsed
        return Dataset.parse_obj(dataset)

    @api_compatibility_check
    def save_settings(self, dataset: Dataset, settings: Settings):
        self.__client__.put(
            f"api/v1/{dataset.task}/{dataset.name}/settings", json=settings
        )

    @api_compatibility_check
    def get_settings(self, dataset: Dataset) -> Settings:
        # Here, we use a new fashion to connect to the Rubrix server api
        return self.__client__.get(f"api/v1/{dataset.task}/{dataset.name}/settings")
