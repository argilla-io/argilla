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

from argilla.client import api
from argilla.client.apis.datasets import (
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
