from rubrix.client import api
from rubrix.client.apis.datasets import (
    Settings,
    TextClassificationSettings,
    TokenClassificationSettings,
)

__all__ = [TextClassificationSettings, TokenClassificationSettings, Settings]


def configure_dataset(name: str, settings: Settings) -> None:
    """
    Configures a dataset with a set of configured labels. If dataset does not
    exist yet, an empty dataset will be created.

    A subset of settings can be provided.

    Args:
        name: The dataset name
        settings: The dataset settings
    """
    active_api = api.active_api()
    datasets = active_api.datasets
    datasets.configure(name, settings=settings)
