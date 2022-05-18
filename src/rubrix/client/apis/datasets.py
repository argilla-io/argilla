from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Set, Union

from pydantic import BaseModel, Field

from rubrix.client.apis import AbstractApi, api_compatibility
from rubrix.client.sdk.commons.errors import AlreadyExistsApiError, NotFoundApiError
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
        label_schema: The label's schema for the dataset

    """

    label_schema: Set[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabelsSchemaSettings":
        label_schema = data.get("label_schema", {})
        labels = {label["name"] for label in label_schema.get("labels", [])}
        return cls(label_schema=labels)


@dataclass
class TextClassificationSettings(LabelsSchemaSettings):
    """
    The settings for text classification datasets

    Args:
        label_schema: The label's schema for the dataset

    """


@dataclass
class TokenClassificationSettings(LabelsSchemaSettings):
    """
    The settings for token classification datasets

    Args:
        label_schema: The label's schema for the dataset

    """


Settings = Union[TextClassificationSettings, TokenClassificationSettings]

__TASK_TO_SETTINGS__ = {
    TaskType.text_classification: TextClassificationSettings,
    TaskType.token_classification: TokenClassificationSettings,
}


class Datasets(AbstractApi):
    """Dataset client api class"""

    _API_PREFIX = "/api/datasets"

    __SETTINGS_MIN_API_VERSION__ = "0.15"

    class _DatasetApiModel(BaseModel):
        name: str
        task: TaskType
        owner: str = None
        created_at: datetime = None
        last_updated: datetime = None

        tags: Dict[str, str] = Field(default_factory=dict)
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class _SettingsApiModel(BaseModel):
        label_schema: Dict[str, Any]

    def find_by_name(self, name: str) -> _DatasetApiModel:
        dataset = get_dataset(self.__client__, name=name).parsed
        return self._DatasetApiModel.parse_obj(dataset)

    def create(self, name: str, settings: Settings):
        task = (
            TaskType.text_classification
            if isinstance(settings, TextClassificationSettings)
            else TaskType.token_classification
        )

        with api_compatibility(self, min_version=self.__SETTINGS_MIN_API_VERSION__):
            dataset = self._DatasetApiModel(name=name, task=task)
            self.__client__.post(f"{self._API_PREFIX}", json=dataset.dict())
            self.__save_settings__(dataset, settings=settings)

    def configure(self, name: str, settings: Settings):
        """
        Configures dataset settings. If dataset does not exist, a new one will be created.
        Pass only settings that want to configure

        Args:
            name: The dataset name
            settings: The dataset settings
        """
        try:
            self.create(name=name, settings=settings)
        except AlreadyExistsApiError:
            ds = self.find_by_name(name)
            self.__save_settings__(dataset=ds, settings=settings)

    def __save_settings__(self, dataset: _DatasetApiModel, settings: Settings):

        if __TASK_TO_SETTINGS__.get(dataset.task) != type(settings):
            raise ValueError(
                f"The provided settings type {type(settings)} cannot be applied to dataset."
                " Task type mismatch"
            )

        settings_ = self._SettingsApiModel(
            label_schema={"labels": [label for label in settings.label_schema]}
        )

        with api_compatibility(self, min_version=self.__SETTINGS_MIN_API_VERSION__):
            self.__client__.put(
                f"{self._API_PREFIX}/{dataset.task}/{dataset.name}/settings",
                json=settings_.dict(),
            )

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
            with api_compatibility(self, min_version=self.__SETTINGS_MIN_API_VERSION__):
                response = self.__client__.get(
                    f"{self._API_PREFIX}/{dataset.task}/{dataset.name}/settings"
                )
                return __TASK_TO_SETTINGS__.get(dataset.task).from_dict(response)
        except NotFoundApiError:
            return None
