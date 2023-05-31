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
    FeedbackItemModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
)


@pytest.fixture
def sdk_client():
    return AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY).httpx


def test_list_datasets(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "get", mocked_client.get)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )

    response = list_datasets(client=sdk_client)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackDatasetModel)


def test_get_datasets(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "get", mocked_client.get)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    response = get_dataset(client=sdk_client, id=dataset_id)
    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == dataset_name


def test_create_dataset(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "post", mocked_client.post)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    response = create_dataset(client=sdk_client, name=dataset_name, workspace_id=workspace_id)
    assert response.status_code == 201
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == dataset_name


def test_delete_dataset(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "delete", mocked_client.delete)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    response = delete_dataset(client=sdk_client, id=dataset_id)
    assert response.status_code == 200

    mocked_response = mocked_client.get("/api/v1/me/datasets")
    assert mocked_response.status_code == 200
    assert len(mocked_response.json()["items"]) < 1


def test_publish_dataset(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "put", mocked_client.put)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/fields",
        json={"name": "test_field", "title": "text_field", "required": True, "settings": {"type": "text"}},
    )
    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/questions",
        json={
            "name": "test_question",
            "title": "text_question",
            "description": "test_description",
            "required": True,
            "settings": {"type": "text"},
        },
    )

    response = publish_dataset(client=sdk_client, id=dataset_id)
    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == dataset_name
    assert response.parsed.status == "ready"


def test_add_field(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "post", mocked_client.post)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    response = add_field(
        client=sdk_client,
        id=dataset_id,
        field={"name": "test_field", "title": "text_field", "required": True, "settings": {"type": "text"}},
    )
    assert response.status_code == 201


def test_get_fields(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "get", mocked_client.get)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/fields",
        json={"name": "test_field", "title": "text_field", "required": True, "settings": {"type": "text"}},
    )

    response = get_fields(client=sdk_client, id=dataset_id)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackFieldModel)


def test_add_question(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "post", mocked_client.post)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    response = add_question(
        client=sdk_client,
        id=dataset_id,
        question={
            "name": "test_question",
            "title": "text_question",
            "description": "test_description",
            "required": True,
            "settings": {"type": "text"},
        },
    )
    assert response.status_code == 201


def test_get_questions(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "get", mocked_client.get)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/questions",
        json={
            "name": "test_question",
            "title": "text_question",
            "description": "test_description",
            "required": True,
            "settings": {"type": "text"},
        },
    )

    response = get_questions(client=sdk_client, id=dataset_id)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackQuestionModel)


def test_add_records(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "post", mocked_client.post)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/fields",
        json={"name": "test_field", "title": "text_field", "required": True, "settings": {"type": "text"}},
    )
    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/questions",
        json={
            "name": "test_question",
            "title": "text_question",
            "description": "test_description",
            "required": True,
            "settings": {"type": "text"},
        },
    )
    mocked_client.put(f"/api/v1/datasets/{dataset_id}/publish")

    response = add_records(client=sdk_client, id=dataset_id, records=[{"fields": {"test_field": "test_value"}}])
    assert response.status_code == 204


def test_get_records(mocked_client, sdk_client, monkeypatch) -> None:
    monkeypatch.setattr(sdk_client, "get", mocked_client.get)

    workspace_name = "test_workspace"
    mocked_response = mocked_client.post(f"/api/workspaces", json={"name": workspace_name})
    workspace_id = mocked_response.json()["id"]

    dataset_name = "test_dataset"
    mocked_response = mocked_client.post(
        f"/api/v1/datasets", json={"name": dataset_name, "guidelines": None, "workspace_id": workspace_id}
    )
    dataset_id = mocked_response.json()["id"]

    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/fields",
        json={"name": "test_field", "title": "text_field", "required": True, "settings": {"type": "text"}},
    )
    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/questions",
        json={
            "name": "test_question",
            "title": "text_question",
            "description": "test_description",
            "required": True,
            "settings": {"type": "text"},
        },
    )
    mocked_client.put(f"/api/v1/datasets/{dataset_id}/publish")
    mocked_client.post(
        f"/api/v1/datasets/{dataset_id}/records", json={"items": [{"fields": {"test_field": "test_value"}}]}
    )

    response = get_records(client=sdk_client, id=dataset_id)
    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackRecordsModel)
    assert len(response.parsed.items) > 0
    assert FeedbackItemModel(**response.parsed.items[0].dict())
