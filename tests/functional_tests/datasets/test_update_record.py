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

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.client.client import Argilla
from argilla.server.apis.v0.models.text2text import Text2TextRecord
from argilla.server.apis.v0.models.text_classification import TextClassificationRecord
from argilla.server.apis.v0.models.token_classification import TokenClassificationRecord
from argilla.server.commons.models import TaskType
from argilla.server.models import User, UserRole
from starlette.testclient import TestClient

from ...factories import UserFactory, WorkspaceFactory
from . import helpers


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.parametrize(
    ("task", "expected_record_class"),
    [
        (TaskType.token_classification, TokenClassificationRecord),
        (TaskType.text_classification, TextClassificationRecord),
        (TaskType.text2text, Text2TextRecord),
    ],
)
def test_update_record_ok(client: TestClient, owner: User, task, expected_record_class, role: UserRole):
    expected_id = 0
    workspace = WorkspaceFactory.create()
    dataset = helpers.create_dataset(Argilla(api_key=owner.api_key, workspace=workspace.name), task=task)
    user = UserFactory.create(role=role, workspaces=[workspace])

    text = "A new value for record 0"
    response = client.patch(
        f"/api/datasets/{dataset}/records/{expected_id}",
        json={"metadata": {"new_value": text}},
        headers={API_KEY_HEADER_NAME: user.api_key},
        params={"workspace": workspace.name},
    )
    assert response.status_code == 200, response.json()
    updated_record = expected_record_class.parse_obj(response.json())
    assert updated_record.metadata["new_value"] == text

    response = client.post(
        f"/api/datasets/{dataset}/{task}:search",
        json={"query": {"ids": [expected_id]}},
        headers={API_KEY_HEADER_NAME: user.api_key},
        params={"workspace": workspace.name},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    record = data["records"][0]

    updated_record.metrics = {}
    assert updated_record == expected_record_class.parse_obj(record)


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.parametrize(
    "task",
    [
        (TaskType.token_classification),
        (TaskType.text_classification),
        (TaskType.text2text),
    ],
)
def test_update_with_not_found(client: TestClient, task: TaskType, role: UserRole):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create(role=role, workspaces=[workspace])

    dataset = helpers.create_dataset(client=Argilla(api_key=user.api_key, workspace=workspace.name), task=task)

    response = client.patch(
        f"/api/datasets/{dataset}/records/not-found",
        json={"status": "Validated"},
        headers={API_KEY_HEADER_NAME: user.api_key},
        params={"workspace": workspace.name},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::RecordNotFound",
            "params": {
                "dataset": f"{workspace.name}.test_dataset",
                "id": "not-found",
                "name": f"{workspace.name}.test_dataset.not-found",
                "type": "Record",
            },
        }
    }


def test_with_wrong_values(client: TestClient, owner: User):
    workspace = WorkspaceFactory.create()
    dataset = helpers.create_dataset(
        client=Argilla(api_key=owner.api_key, workspace=workspace.name), task=TaskType.text_classification
    )

    response = client.patch(
        f"/api/datasets/{dataset}/records/not-found",
        json={"status": "NOStatus"},
        headers={API_KEY_HEADER_NAME: owner.api_key},
        params={"workspace": workspace.name},
    )

    assert response.status_code == 422
