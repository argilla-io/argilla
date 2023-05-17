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

import httpx
import pytest
from argilla._constants import DEFAULT_API_KEY
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.v1.datasets.api import (
    add_field,
    add_question,
    add_records,
    create_dataset,
    delete_dataset,
    get_dataset,
    get_fields,
    get_questions,
    get_records,
    list_datasets,
    publish_dataset,
)
from argilla.client.sdk.v1.datasets.models import (
    FeedbackDatasetModel,
    FeedbackFieldModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
)


@pytest.fixture
def sdk_client():
    return AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY)


def test_list_datasets(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(httpx, "get", mocked_client.get)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_client.post(f"/api/v1/datasets", json={"name": dataset_name, "guidelines": "", "workspace_id": workspace_id})

    response = list_datasets(client=sdk_client)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackDatasetModel)
