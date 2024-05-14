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
import logging
import warnings
from typing import Optional

from argilla.client import singleton
from argilla.client.apis.datasets import Settings, TextClassificationSettings, TokenClassificationSettings

__all__ = [TextClassificationSettings, TokenClassificationSettings, Settings]

_LOGGER = logging.getLogger(__name__)


def load_dataset_settings(name: str, workspace: Optional[str] = None) -> Optional[Settings]:
    """
    Loads the settings of a dataset

    Args:
        name: The dataset name
        workspace: The workspace name where the dataset belongs to

    Returns:
        The dataset settings
    """
    active_api = singleton.active_api()
    datasets = active_api.datasets

    settings = datasets.load_settings(name, workspace=workspace)
    if settings is None:
        return None
    else:
        return settings


def configure_dataset_settings(name: str, settings: Settings, workspace: Optional[str] = None) -> None:
    """
    Configures a dataset with a set of configured labels. If dataset does not
    exist yet, an empty dataset will be created.

    A subset of settings can be provided.

    Args:
        name: The dataset name
        settings: The dataset settings
        workspace: The workspace name where the dataset will belongs to
    """
    active_api = singleton.active_api()
    datasets = active_api.datasets
    datasets.configure(name, workspace=workspace or active_api.get_workspace(), settings=settings)


def configure_dataset(name: str, settings: Settings, workspace: Optional[str] = None) -> None:
    """
    Configures a dataset with a set of configured labels. If dataset does not
    exist yet, an empty dataset will be created.

    A subset of settings can be provided.

    Args:
        name: The dataset name
        settings: The dataset settings
        workspace: The workspace name where the dataset will belongs to
    """
    warnings.warn("This method is deprecated. Use configure_dataset_settings instead.", DeprecationWarning)
    return configure_dataset_settings(name, settings, workspace)
