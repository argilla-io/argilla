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
from argilla.server.models import User, UserRole
from argilla.server.schemas.datasets import Dataset
from starlette.testclient import TestClient

from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    UserFactory,
    WorkspaceFactory,
    WorkspaceUserFactory,
)


def delete_dataset(client: TestClient, dataset_name: str, workspace: str, headers: Dict[str, Any]):
    url = f"/api/datasets/{dataset_name}?workspace={workspace}"

    assert client.delete(url, headers=headers).status_code == 200


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


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
def test_delete_dataset(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory(role=role, workspaces=[dataset.workspace])
    api_auth_headers = {API_KEY_HEADER_NAME: user.api_key}

    create_mock_dataset(client, dataset_name=dataset.name, workspace=dataset.workspace.name, headers=owner_auth_header)

    delete_dataset(client, dataset_name=dataset.name, workspace=dataset.workspace.name, headers=api_auth_headers)
    response = client.get(f"/api/datasets/{dataset.name}?workspace={dataset.workspace.name}", headers=api_auth_headers)

    assert response.status_code == 404, response.json()

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::EntityNotFoundError",
            "params": {"name": dataset.name, "type": "ServiceDataset"},
        }
    }


def test_delete_dataset_with_missing_workspace(client: TestClient, owner_auth_header: dict):
    response = client.delete("/api/datasets/dataset", headers=owner_auth_header)

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::MissingInputParamError",
            "params": {"message": "A workspace must be provided"},
        }
    }


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
def test_create_dataset(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    workspace_name = dataset.workspace.name
    delete_dataset(client, dataset_name=dataset.name, workspace=workspace_name, headers=owner_auth_header)

    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    request = dict(
        name=dataset.name,
        task=TaskType.text_classification,
        tags={"env": "test", "class": "text classification"},
        metadata={"config": {"the": "config"}},
    )

    response = client.post(
        f"/api/datasets?workspace={workspace_name}", json=request, headers={API_KEY_HEADER_NAME: user.api_key}
    )
    assert response.status_code == 200

    created_dataset = Dataset.parse_obj(response.json())

    assert created_dataset.id
    assert created_dataset.created_by == user.username
    assert created_dataset.metadata == request["metadata"]
    assert created_dataset.tags == request["tags"]
    assert created_dataset.name == dataset.name
    assert created_dataset.workspace == workspace_name
    assert created_dataset.task == TaskType.text_classification


def test_create_dataset_with_already_created_error(client: TestClient, owner_auth_header: dict):
    workspace = WorkspaceFactory.create()
    dataset = DatasetFactory.create()

    create_mock_dataset(client, dataset_name=dataset.name, headers=owner_auth_header, workspace=workspace.name)

    response = client.post(
        f"/api/datasets?workspace={workspace.name}",
        json={"name": dataset.name, "task": TaskType.text_classification},
        headers=owner_auth_header,
    )
    assert response.status_code == 409


def test_create_workspace_with_missing_workspace(client: TestClient, owner_auth_header: dict):
    dataset_name = "missing-workspace-dataset"

    response = client.post(
        "/api/datasets", json={"name": dataset_name, "task": TaskType.text_classification}, headers=owner_auth_header
    )

    assert response.status_code == 400


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
def test_create_dataset_using_several_workspaces(client: TestClient, role: UserRole):
    user = UserFactory.create(workspaces=WorkspaceFactory.create_batch(3), role=role)
    user_auth_headers = {API_KEY_HEADER_NAME: user.api_key}

    dataset_name = "test_dataset"

    other_workspace = user.workspaces[0]
    for workspace in user.workspaces[1:]:
        delete_dataset(client, dataset_name=dataset_name, workspace=workspace.name, headers=user_auth_headers)
        delete_dataset(client, dataset_name=dataset_name, workspace=other_workspace.name, headers=user_auth_headers)

        request = dict(name=dataset_name, task=TaskType.text_classification)
        response = client.post(f"/api/datasets?workspace={workspace.name}", json=request, headers=user_auth_headers)

        assert response.status_code == 200, response.json()

        dataset = Dataset.parse_obj(response.json())

        assert dataset.created_by == user.username
        assert dataset.name == dataset_name
        assert dataset.owner == workspace.name
        assert dataset.task == TaskType.text_classification

        response = client.post(f"/api/datasets?workspace={workspace.name}", json=request, headers=user_auth_headers)

        assert response.status_code == 409, response.json()

        response = client.post(
            f"/api/datasets?workspace={other_workspace.name}", json=request, headers=user_auth_headers
        )

        assert response.status_code == 200, response.json()

        dataset = Dataset.parse_obj(response.json())

        assert dataset.created_by == user.username
        assert dataset.name == dataset_name
        assert dataset.workspace == other_workspace.name
        assert dataset.task == TaskType.text_classification


@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification, TaskType.text2text])
def test_dataset_naming_validation(client: TestClient, owner_auth_header: dict, task):
    request = TextClassificationBulkRequest(records=[])
    dataset_name = "Wrong dataset name"

    workspace = WorkspaceFactory.create()

    response = client.post(
        f"/api/datasets/{dataset_name}/{task}:bulk?workspace={workspace.name}",
        json=request.dict(by_alias=True),
        headers=owner_auth_header,
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


def test_list_datasets(client: TestClient, owner_auth_header: dict):
    workspace = WorkspaceFactory.create()
    dataset = DatasetFactory.create()
    create_mock_dataset(client, dataset_name=dataset.name, headers=owner_auth_header, workspace=workspace.name)

    response = client.get(f"/api/datasets?workspace={workspace.name}", headers=owner_auth_header)
    assert response.status_code == 200

    datasets = [Dataset.parse_obj(item) for item in response.json()]
    assert len(datasets) > 0

    assert dataset.name in [ds.name for ds in datasets]
    for ds in datasets:
        assert ds.id


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
def test_list_datasets_without_workspace(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    create_mock_dataset(client, dataset.name, headers=owner_auth_header, workspace=dataset.workspace.name)
    response = client.get("/api/datasets", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
def test_update_dataset(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    workspace_name = dataset.workspace.name
    create_mock_dataset(client, dataset_name=dataset.name, headers=owner_auth_header, workspace=workspace_name)

    user = UserFactory.create(role=role, workspaces=[dataset.workspace])
    response = client.patch(
        f"/api/datasets/{dataset.name}?workspace={workspace_name}",
        json={"metadata": {"new": "value"}},
        headers={API_KEY_HEADER_NAME: user.api_key},
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/datasets/{dataset.name}?workspace={workspace_name}", headers={API_KEY_HEADER_NAME: user.api_key}
    )
    assert response.status_code == 200, response.json()

    ds = Dataset.parse_obj(response.json())
    assert ds.metadata["new"] == "value"


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
def test_update_dataset_without_permissions(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    workspace_name = dataset.workspace.name
    create_mock_dataset(client, dataset_name=dataset.name, headers=owner_auth_header, workspace=workspace_name)

    user = UserFactory.create(role=role)

    response = client.patch(
        f"/api/datasets/{dataset.name}?workspace={workspace_name}",
        json={"metadata": {"new": "metadata"}},
        headers={API_KEY_HEADER_NAME: user.api_key},
    )

    assert response.status_code == 403


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
def test_update_dataset_by_annotator_without_changes(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    workspace_name = dataset.workspace.name
    create_mock_dataset(client, dataset_name=dataset.name, headers=owner_auth_header, workspace=workspace_name)

    user = UserFactory.create(workspaces=[dataset.workspace])

    response = client.get(
        f"/api/datasets/{dataset.name}?workspace={workspace_name}", headers={API_KEY_HEADER_NAME: user.api_key}
    )
    assert response.status_code == 200

    created_dataset = response.json()
    created_dataset.pop("last_updated")

    response = client.patch(
        f"/api/datasets/{dataset.name}?workspace={workspace_name}",
        json={},
        headers={API_KEY_HEADER_NAME: user.api_key},
    )

    assert response.status_code == 200

    updated_dataset = response.json()
    updated_dataset.pop("last_updated")

    assert updated_dataset == created_dataset


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
def test_open_and_close_dataset(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    workspace_name = dataset.workspace.name
    create_mock_dataset(client, dataset_name=dataset.name, headers=owner_auth_header, workspace=workspace_name)

    user = UserFactory.create(role=role, workspaces=[dataset.workspace])
    endpoint_url = f"/api/datasets/{dataset.name}:{{action}}?workspace={workspace_name}"

    assert client.put(endpoint_url.format(action="close"), headers=owner_auth_header).status_code == 200

    response = client.post(
        f"/api/datasets/{dataset.name}/TextClassification:search?workspace={workspace_name}",
        headers={API_KEY_HEADER_NAME: user.api_key},
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": {"code": "argilla.api.errors::ClosedDatasetError", "params": {"name": dataset.name}}
    }

    response = client.put(endpoint_url.format(action="open"), headers={API_KEY_HEADER_NAME: user.api_key})
    assert response.status_code == 200

    response = client.post(
        f"/api/datasets/{dataset.name}/TextClassification:search?workspace={workspace_name}",
        headers=owner_auth_header,
    )
    assert response.status_code == 200


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
def test_delete_records(client: TestClient, owner_auth_header: dict, role: UserRole):
    dataset = DatasetFactory.create()
    records = [{"id": i, "inputs": {"text": f"This is a text for id {i}"}} for i in range(1, 100)]
    workspace_name = dataset.workspace.name
    create_mock_dataset(
        client, dataset_name=dataset.name, workspace=workspace_name, headers=owner_auth_header, records=records
    )

    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    response = client.request(
        "DELETE",
        url=f"/api/datasets/{dataset.name}/data?workspace={workspace_name}",
        json={"ids": [1]},
        headers={API_KEY_HEADER_NAME: user.api_key},
    )

    assert response.status_code == 200
    assert response.json() == {"matched": 1, "processed": 1}

    response = client.delete(
        f"/api/datasets/{dataset.name}/data?mark_as_discarded=true&workspace={workspace_name}",
        headers={API_KEY_HEADER_NAME: user.api_key},
    )

    assert response.status_code == 200
    assert response.json() == {"matched": 99, "processed": 98}  # different values are caused by conflicts found


def test_delete_records_as_annotator(client: TestClient, owner_auth_header: dict):
    dataset = DatasetFactory.create()
    records = [{"id": i, "inputs": {"text": f"This is a text for id {i}"}} for i in range(1, 100)]
    workspace_name = dataset.workspace.name
    create_mock_dataset(
        client, dataset_name=dataset.name, workspace=workspace_name, headers=owner_auth_header, records=records
    )

    user = AnnotatorFactory.create(workspaces=[dataset.workspace])

    response = client.delete(
        f"/api/datasets/{dataset.name}/data?workspace={workspace_name}",
        headers={API_KEY_HEADER_NAME: user.api_key},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ForbiddenOperationError",
            "params": {
                "detail": "You don't have the necessary permissions to delete records on this dataset."
                " Only administrators can delete datasets"
            },
        }
    }

    response = client.delete(
        f"/api/datasets/{dataset.name}/data",
        headers={API_KEY_HEADER_NAME: user.api_key},
        params={
            "mark_as_discarded": True,
            "workspace": workspace_name,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"matched": 99, "processed": 99}  # different values are caused by conflicts found
