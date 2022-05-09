from rubrix.client import api
from rubrix.client.apis.datasets import (
    Settings,
    TextClassificationSettings,
    TokenClassificationSettings,
)

__all__ = [TextClassificationSettings, TokenClassificationSettings, Settings]


def create_dataset(name: str, settings: Settings) -> None:
    """
    Creates a new with a set of configured labels

    Args:
        name: The dataset name
        settings: The dataset settings
    """
    active_api = api.active_api()
    datasets = active_api.datasets
    datasets.create(name, settings=settings)
