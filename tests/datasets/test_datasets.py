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

import argilla as rg
import pytest
from argilla import TextClassificationSettings, TokenClassificationSettings
from argilla.client import api
from argilla.client.client import Argilla
from argilla.client.sdk.commons.errors import ForbiddenApiError


@pytest.mark.parametrize(
    ("settings_", "wrong_settings"),
    [
        (
            TextClassificationSettings(label_schema={"A", "B"}),
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
        ),
        (
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
            TextClassificationSettings(label_schema={"A", "B"}),
        ),
    ],
)
def test_settings_workflow(mocked_client, settings_, wrong_settings):
    dataset = "test-dataset"
    rg.delete(dataset)
    rg.configure_dataset(dataset, settings=settings_)

    current_api = api.active_api()
    datasets_api = current_api.datasets

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    settings_.label_schema = {"LALALA"}
    rg.configure_dataset(dataset, settings_)

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    with pytest.raises(ValueError, match="Task type mismatch"):
        rg.configure_dataset(dataset, wrong_settings)


def test_list_dataset(mocked_client):
    from argilla.client.api import active_client

    client = active_client()
    datasets = client.http_client.get("/api/datasets")

    for ds in datasets:
        assert ds["owner"] == ds["workspace"]


@pytest.mark.skip(reason="Factory users is not working for users sharing workspaces")
def test_delete_dataset_by_non_creator(mocked_client, mock_user):
    dataset = "test_delete_dataset_by_non_creator"

    rg = Argilla()

    rg.delete(dataset)
    rg.datasets.configure(dataset, settings=TextClassificationSettings(label_schema={"A", "B", "C"}))

    api = Argilla(api_key=mock_user.api_key, workspace="argilla")
    with pytest.raises(ForbiddenApiError):
        api.delete(dataset)
