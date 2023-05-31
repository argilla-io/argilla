#  coding=utf-8
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
from typing import Any, Dict, List

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
)
from argilla.server.commons.models import TaskType
from argilla.server.models import User
from argilla.server.schemas.datasets import Dataset
from starlette.testclient import TestClient

from tests.factories import WorkspaceUserFactory


@pytest.fixture(scope="function")
def dataset_name(client: TestClient, argilla_user: User, argilla_auth_header: dict):
    dataset_name = "test_dataset"
    try:
        client.delete(f"/api/datasets/{dataset_name}?workspace={argilla_user.username}", headers=argilla_auth_header)
        yield dataset_name
    finally:
        client.delete(
            f"/api/datasets/{dataset_name}?workspace={argilla_user.username}",
            headers=argilla_auth_header,
        )


def delete_dataset(client: TestClient, dataset_name, workspace: str, headers: Dict[str, Any]):
    url = f"/api/datasets/{dataset_name}?workspace={workspace}"

    client.delete(url, headers=headers)


def create_mock_dataset(
    client: TestClient, dataset_name: str, headers: Dict[str, Any], workspace: str, records: List = None
):
    url = f"/api/datasets/{dataset_name}/TextClassification:bulk?workspace={workspace}"

    bulk_data = TextClassificationBulkRequest(
        tags={"env": "test", "class": "text classification"},
        metadata={"config": {"the": "config"}},
        records=records or [],
    ).dict(by_alias=True)

    response = client.post(url, json=bulk_data, headers=headers)
    assert response.status_code == 200, response.json()


def test_delete_dataset(client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str):
    workspace_name = argilla_user.username

    create_mock_dataset(client, dataset_name=dataset_name, workspace=workspace_name, headers=argilla_auth_header)

    delete_dataset(client, dataset_name=dataset_name, workspace=workspace_name, headers=argilla_auth_header)

    response = client.get(f"/api/datasets/{dataset_name}?workspace={workspace_name}", headers=argilla_auth_header)
    assert response.status_code == 404, response.json()

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::EntityNotFoundError",
            "params": {"name": dataset_name, "type": "ServiceDataset"},
        }
    }


def test_delete_dataset_with_missing_workspace(client: TestClient, argilla_user: User, argilla_auth_header: dict):
    response = client.delete("/api/datasets/dataset", headers=argilla_auth_header)

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::MissingInputParamError",
            "params": {"message": "A workspace must be provided"},
        }
    }


def test_create_dataset(client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str):
    workspace_name = argilla_user.username

    request = dict(
        name=dataset_name,
        task=TaskType.text_classification,
        tags={"env": "test", "class": "text classification"},
        metadata={"config": {"the": "config"}},
    )

    response = client.post(f"/api/datasets?workspace={workspace_name}", json=request, headers=argilla_auth_header)
    assert response.status_code == 200

    dataset = Dataset.parse_obj(response.json())

    assert dataset.id
    assert dataset.created_by == argilla_user.username
    assert dataset.metadata == request["metadata"]
    assert dataset.tags == request["tags"]
    assert dataset.name == dataset_name
    assert dataset.workspace == workspace_name
    assert dataset.task == TaskType.text_classification


def test_create_dataset_with_already_created_error(
    client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str
):
    workspace_name = argilla_user.username

    create_mock_dataset(client, dataset_name=dataset_name, headers=argilla_auth_header, workspace=workspace_name)

    response = client.post(
        f"/api/datasets?workspace={workspace_name}",
        json={"name": dataset_name, "task": TaskType.text_classification},
        headers=argilla_auth_header,
    )
    assert response.status_code == 409


def test_create_workspace_with_missing_workspace(client: TestClient, argilla_user: User, argilla_auth_header: dict):
    dataset_name = "missing-workspace-dataset"

    response = client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": TaskType.text_classification},
        headers=argilla_auth_header,
    )

    assert response.status_code == 400


def test_create_dataset_using_several_workspaces(
    client: TestClient, argilla_user: User, mock_user: User, argilla_auth_header: dict, dataset_name: str
):
    mock_auth_headers = {API_KEY_HEADER_NAME: mock_user.api_key}
    for workspace in mock_user.workspaces:
        delete_dataset(client, dataset_name=dataset_name, workspace=workspace.name, headers=mock_auth_headers)

        request = dict(name=dataset_name, task=TaskType.text_classification)

        workspace = workspace.name
        response = client.post(f"/api/datasets?workspace={workspace}", json=request, headers=mock_auth_headers)

        assert response.status_code == 200, response.json()

        dataset = Dataset.parse_obj(response.json())

        assert dataset.created_by == mock_user.username
        assert dataset.name == dataset_name
        assert dataset.owner == workspace
        assert dataset.task == TaskType.text_classification

        response = client.post(f"/api/datasets?workspace={workspace}", json=request, headers=mock_auth_headers)

        assert response.status_code == 409, response.json()

        another_ws = None
        for ws in mock_user.workspaces:
            if ws.name != workspace:
                another_ws = ws.name
                break

        response = client.post(f"/api/datasets?workspace={another_ws}", json=request, headers=mock_auth_headers)

        assert response.status_code == 200, response.json()

        dataset = Dataset.parse_obj(response.json())

        assert dataset.created_by == mock_user.username
        assert dataset.name == dataset_name
        assert dataset.workspace == another_ws
        assert dataset.task == TaskType.text_classification


@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification, TaskType.text2text])
def test_dataset_naming_validation(client: TestClient, argilla_user: User, argilla_auth_header: dict, task):
    request = TextClassificationBulkRequest(records=[])
    dataset_name = "Wrong dataset name"

    response = client.post(
        f"/api/datasets/{dataset_name}/{task}:bulk?workspace={argilla_user.username}",
        json=request.dict(by_alias=True),
        headers=argilla_auth_header,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ValidationError",
            "params": {
                "errors": [
                    {
                        "ctx": {"pattern": "^(?!-|_)[a-z0-9-_]+$"},
                        "loc": ["name"],
                        "msg": "string does not match regex " '"^(?!-|_)[a-z0-9-_]+$"',
                        "type": "value_error.str.regex",
                    }
                ],
                "model": "CreateDatasetRequest",
            },
        }
    }


def test_list_datasets(client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str):
    create_mock_dataset(client, dataset_name=dataset_name, headers=argilla_auth_header, workspace=argilla_user.username)

    response = client.get(f"/api/datasets?workspace={argilla_user.username}", headers=argilla_auth_header)
    assert response.status_code == 200

    datasets = [Dataset.parse_obj(item) for item in response.json()]
    assert len(datasets) > 0

    assert dataset_name in [ds.name for ds in datasets]
    for ds in datasets:
        assert ds.id


def test_list_datasets_without_workspace(client: TestClient, argilla_user: User, argilla_auth_header: dict):
    response = client.get("/api/datasets", headers=argilla_auth_header)

    assert response.status_code == 200


def test_update_dataset(client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str):
    create_mock_dataset(client, dataset_name=dataset_name, headers=argilla_auth_header, workspace=argilla_user.username)

    response = client.patch(
        f"/api/datasets/{dataset_name}?workspace={argilla_user.username}",
        json={"metadata": {"new": "value"}},
        headers=argilla_auth_header,
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/datasets/{dataset_name}?workspace={argilla_user.username}", headers=argilla_auth_header
    )
    assert response.status_code == 200, response.json()

    ds = Dataset.parse_obj(response.json())
    assert ds.metadata["new"] == "value"


def test_update_dataset_by_annotator(
    client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str, annotator: User
):
    workspace_name = argilla_user.username

    for workspace in argilla_user.workspaces:
        if workspace.name == workspace_name:
            WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=annotator.id)
            break

    create_mock_dataset(client, dataset_name=dataset_name, headers=argilla_auth_header, workspace=workspace_name)

    response = client.patch(
        f"/api/datasets/{dataset_name}?workspace={workspace_name}",
        json={"metadata": {"new": "metadata"}},
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 200


def test_update_dataset_by_annotator_without_permissions(
    client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str, annotator: User
):
    create_mock_dataset(client, dataset_name=dataset_name, headers=argilla_auth_header, workspace=argilla_user.username)

    response = client.patch(
        f"/api/datasets/{dataset_name}?workspace={argilla_user.username}",
        json={"metadata": {"new": "metadata"}},
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403


def test_update_dataset_by_annotator_without_changes(
    client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str, annotator: User
):
    for workspace in argilla_user.workspaces:
        WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=annotator.id)

    create_mock_dataset(client, dataset_name=dataset_name, headers=argilla_auth_header, workspace=argilla_user.username)

    response = client.get(
        f"/api/datasets/{dataset_name}?workspace={argilla_user.username}", headers=argilla_auth_header
    )
    assert response.status_code == 200

    created_dataset = response.json()
    created_dataset.pop("last_updated")

    response = client.patch(
        f"/api/datasets/{dataset_name}?workspace={argilla_user.username}",
        json={},
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 200

    updated_dataset = response.json()
    updated_dataset.pop("last_updated")

    assert updated_dataset == created_dataset


def test_open_and_close_dataset(client: TestClient, argilla_user: User, argilla_auth_header: dict, dataset_name: str):
    workspace_name = argilla_user.username
    endpoint_url = f"/api/datasets/{dataset_name}:{{action}}?workspace={workspace_name}"

    create_mock_dataset(client, dataset_name=dataset_name, workspace=workspace_name, headers=argilla_auth_header)

    assert client.put(endpoint_url.format(action="close"), headers=argilla_auth_header).status_code == 200

    response = client.post(
        f"/api/datasets/{dataset_name}/TextClassification:search?workspace={workspace_name}",
        headers=argilla_auth_header,
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": {"code": "argilla.api.errors::ClosedDatasetError", "params": {"name": dataset_name}}
    }

    assert client.put(endpoint_url.format(action="open"), headers=argilla_auth_header).status_code == 200
    assert (
        client.post(
            f"/api/datasets/{dataset_name}/TextClassification:search?workspace={workspace_name}",
            headers=argilla_auth_header,
        ).status_code
        == 200
    )


def test_delete_records(
    client: TestClient, argilla_user: User, mock_user: User, argilla_auth_header: dict, dataset_name: str
):
    for workspace in argilla_user.workspaces:
        WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=mock_user.id)

    create_mock_dataset(
        client,
        dataset_name=dataset_name,
        workspace=argilla_user.username,
        headers=argilla_auth_header,
        records=[
            {
                "id": i,
                "inputs": {"text": f"This is a text for id {i}"},
            }
            for i in range(1, 100)
        ],
    )
    response = client.request(
        "DELETE",
        url=f"/api/datasets/{dataset_name}/data?workspace={argilla_user.username}",
        json={"ids": [1]},
        headers=argilla_auth_header,
    )

    assert response.status_code == 200
    assert response.json() == {"matched": 1, "processed": 1}

    response = client.delete(
        f"/api/datasets/{dataset_name}/data?workspace={argilla_user.username}",
        headers={API_KEY_HEADER_NAME: mock_user.api_key},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ForbiddenOperationError",
            "params": {
                "detail": "You don't have the necessary permissions to delete records on this dataset."
                " Only dataset creators or administrators can delete datasets"
            },
        }
    }

    response = client.delete(
        f"/api/datasets/{dataset_name}/data?mark_as_discarded=true&workspace={argilla_user.username}",
        headers={API_KEY_HEADER_NAME: mock_user.api_key},
    )

    assert response.status_code == 200
    assert response.json() == {"matched": 99, "processed": 98}  # different values are caused by conflicts found
