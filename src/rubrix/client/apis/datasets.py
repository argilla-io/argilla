from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Set, Union

from pydantic import BaseModel, Field

from rubrix.client.apis.base import AbstractApi, api_compatibility_check
from rubrix.client.sdk.commons.errors import NotFoundApiError
from rubrix.client.sdk.datasets.api import get_dataset
from rubrix.client.sdk.datasets.models import TaskType


@dataclass
class _AbstractSettings:
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "_AbstractSettings":
        """
        Creates a settings instance from a plain python dictionary

        Args:
            data: The data dict

        Returns:
            A new ``cls`` settings instance
        """
        raise NotImplementedError()


@dataclass
class LabelsSchemaSettings(_AbstractSettings):
    """
    A base dataset settings class for labels schema management

    Args:
        labels_schema: The label's schema for the dataset

    """

    labels_schema: Set[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabelsSchemaSettings":
        labels_schema = data.get("labels_schema", {})
        labels = {label["name"] for label in labels_schema.get("labels", [])}
        return cls(labels_schema=labels)


@dataclass
class TextClassificationSettings(LabelsSchemaSettings):
    """
    The settings for text classification datasets

    Args:
        labels_schema: The label's schema for the dataset

    """


@dataclass
class TokenClassificationSettings(LabelsSchemaSettings):
    """
    The settings for token classification datasets

    Args:
        labels_schema: The label's schema for the dataset

    """


Settings = Union[TextClassificationSettings, TokenClassificationSettings]

__TASK_TO_SETTINGS__ = {
    TaskType.text_classification: TextClassificationSettings,
    TaskType.token_classification: TokenClassificationSettings,
}


class Datasets(AbstractApi):
    """Dataset client api class"""

    _API_PREFIX = "/api/datasets"

    __SETTINGS_MIN_API_VERSION__ = "0.15.0"

    class _DatasetApiModel(BaseModel):
        name: str
        task: TaskType
        owner: str = None
        created_at: datetime = None
        last_updated: datetime = None

        tags: Dict[str, str] = Field(default_factory=dict)
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class _SettingsApiModel(BaseModel):
        labels_schema: Dict[str, Any]

    def find_by_name(self, name: str) -> _DatasetApiModel:
        dataset = get_dataset(self.__client__, name=name).parsed
        return self._DatasetApiModel.parse_obj(dataset)

    @api_compatibility_check(min_version=__SETTINGS_MIN_API_VERSION__)
    def create(self, name: str, settings: Settings):
        task = (
            TaskType.text_classification
            if isinstance(settings, TextClassificationSettings)
            else TaskType.token_classification
        )

        dataset = self._DatasetApiModel(name=name, task=task)
        self.__client__.post(f"{self._API_PREFIX}/", json=dataset.dict())
        self.save_settings(dataset, settings=settings)

    @api_compatibility_check(min_version=__SETTINGS_MIN_API_VERSION__)
    def save_settings(self, dataset: _DatasetApiModel, settings: Settings):
        settings_ = self._SettingsApiModel(
            labels_schema={"labels": [label for label in settings.labels_schema]}
        )

        # TODO: use the api compatiblity check as a with block (passing the abstract api and the minimal version
        self.__client__.put(
            f"{self._API_PREFIX}/{dataset.task}/{dataset.name}/settings",
            json=settings_.dict(),
        )

    @api_compatibility_check(min_version=__SETTINGS_MIN_API_VERSION__)
    def load_settings(self, name: str) -> Optional[Settings]:
        """
        Load the dataset settings

        Args:
            name: The dataset name

        Returns:
            Settings defined for the dataset
        """
        dataset = self.find_by_name(name)
        try:
            response = self.__client__.get(
                f"{self._API_PREFIX}/{dataset.task}/{dataset.name}/settings"
            )
            return __TASK_TO_SETTINGS__.get(dataset.task).from_dict(response)
        except NotFoundApiError:
            return None
