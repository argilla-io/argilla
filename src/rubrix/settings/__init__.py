from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Set, Union

from rubrix.client import api
from rubrix.client._apis.datasets import Settings as _Settings
from rubrix.client.sdk.commons.errors import NotFoundApiError
from rubrix.client.sdk.datasets.models import TaskType
from rubrix.settings._base import AbstractSettings, LabelsSchema


@dataclass
class TextClassificationSettings(AbstractSettings):
    """
    The settings for text classification datasets

    Args:
        labels_schema: The label's schema for the dataset

    """

    labels_schema: Union[Set[str], LabelsSchema]

    def __post_init__(self):
        if isinstance(self.labels_schema, Set):
            self.labels_schema = LabelsSchema.from_labels_set(self.labels_schema)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextClassificationSettings":
        return cls(labels_schema=data.get("labels_schema", set()))


@dataclass
class TokenClassificationSettings(AbstractSettings):
    """
    The settings for token classification datasets

    Args:
        labels_schema: The label's schema for the dataset

    """

    labels_schema: Union[Set[str], LabelsSchema]

    def __post_init__(self):
        if isinstance(self.labels_schema, Set):
            self.labels_schema = LabelsSchema.from_labels_set(self.labels_schema)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenClassificationSettings":
        return cls(labels_schema=data.get("labels_schema", set()))


Settings = Union[TextClassificationSettings, TokenClassificationSettings]


def save_settings(name: str, settings: Settings):
    """
    Save provided settings for a dataset. If dataset does not exist, it will be created
    with those settings

    Args:
        name: The dataset name
        settings: The dataset settings

    Returns:
        None
    """
    if not isinstance(
        settings, (TokenClassificationSettings, TextClassificationSettings)
    ):
        return

    _settings = _Settings.parse_obj(asdict(settings))

    active_api = api.active_api()
    datasets = active_api.datasets

    try:
        dataset = datasets.find_by_name(name)
        datasets.save_settings(dataset, _settings)
    except NotFoundApiError:
        # TODO: find a normalized way to show a message here
        task = (
            TaskType.text_classification
            if isinstance(settings, TextClassificationSettings)
            else TaskType.token_classification
        )
        datasets.create(name, task=task, settings=_settings)


def load_settings(name: str) -> Optional[Settings]:
    """
    Load the dataset settings

    Args:
        name: The dataset name

    Returns:
        Settings defined for the dataset
    """
    active_api = api.active_api()

    datasets = active_api.datasets
    dataset = datasets.find_by_name(name)
    settings = datasets.get_settings(dataset)

    settings_class = None
    if TaskType.text_classification == dataset.task:
        settings_class = TextClassificationSettings
    elif TaskType.text_classification == dataset.task:
        settings_class = TextClassificationSettings

    if settings_class and settings:
        return settings_class.from_dict(settings.dict())
