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
from typing import TYPE_CHECKING, Any, Optional

import pytest
from argilla_server.commons.models import TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User

from tests.factories import AnnotatorFactory, WorkspaceFactory

if TYPE_CHECKING:
    from httpx import AsyncClient


async def create_dataset(client: "AsyncClient", name: str, workspace_name: str):
    response = await client.post(
        "/api/datasets",
        json={"name": name, "workspace": workspace_name, "task": TaskType.text_classification},
    )
    assert response.status_code == 200


async def delete_dataset(client: "AsyncClient", name: str, workspace_name: str):
    response = await client.delete(f"/api/datasets/{name}", params={"workspace": workspace_name})
    assert response.status_code == 200


async def create_settings(async_client: "AsyncClient", name: str, workspace_name: str, labels: Optional[list] = None):
    response = await async_client.put(
        f"/api/datasets/{TaskType.text_classification}/{name}/settings",
        json={"label_schema": {"labels": labels or ["Label1", "Label2"]}},
        params={"workspace": workspace_name},
    )
    return response


async def fetch_settings(async_client: "AsyncClient", name: str, workspace_name: str):
    response = await async_client.get(
        f"/api/datasets/{TaskType.text_classification}/{name}/settings", params={"workspace": workspace_name}
    )
    return response


async def log_some_data(async_client: "AsyncClient", name: str, workspace_name: str):
    response = await async_client.post(
        f"/api/datasets/{name}/TextClassification:bulk",
        json={
            "records": [
                {
                    "inputs": {"data": "my data"},
                    "prediction": {
                        "agent": "test",
                        "labels": [
                            {"class": "Mocking", "score": 0.2},
                        ],
                    },
                }
            ]
        },
        params={"workspace": workspace_name},
    )
    return response


@pytest.mark.parametrize("labels", [["Label1", "Label2"], ["1", "2", "3"], [1, 2, 3, 4]])
@pytest.mark.asyncio
async def test_create_dataset_settings(async_client: "AsyncClient", argilla_user: User, labels: list):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_name = argilla_user.username

    name = "test_create_dataset_settings"
    await delete_dataset(async_client, name, workspace_name=workspace_name)
    await create_dataset(async_client, name, workspace_name=workspace_name)

    response = await create_settings(async_client, name, workspace_name=workspace_name, labels=["Label1", "Label2"])
    assert response.status_code == 200

    created = response.json()

    response = await fetch_settings(async_client, name, workspace_name=workspace_name)
    assert response.json() == created


@pytest.mark.asyncio
async def test_get_dataset_settings_not_found(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    name = "test_get_dataset_settings"
    workspace = argilla_user.username

    await delete_dataset(async_client, name, workspace)
    await create_dataset(async_client, name, workspace)

    response = await fetch_settings(async_client, name, workspace)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_settings(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    name = "test_delete_settings"
    workspace = argilla_user.username

    await delete_dataset(async_client, name, workspace)
    await create_dataset(async_client, name, workspace)

    response = await create_settings(async_client, name, workspace)
    assert response.status_code == 200

    response = await async_client.delete(
        f"/api/datasets/{TaskType.text_classification}/{name}/settings", params={"workspace": workspace}
    )
    assert response.status_code == 200

    response = await fetch_settings(async_client, name, workspace)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validate_settings_when_logging_data(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    name = "test_validate_settings_when_logging_data"
    workspace = argilla_user.username

    await delete_dataset(async_client, name, workspace)
    await create_dataset(async_client, name, workspace)

    response = await create_settings(async_client, name, workspace)
    assert response.status_code == 200

    response = await log_some_data(async_client, name, workspace)
    assert response.status_code == 400

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "Provided records contain the Mocking label, "
                "that is not included in the labels schema.\n"
                "Please, annotate your records using labels "
                "defined in the labels schema."
            },
        }
    }


@pytest.mark.asyncio
async def test_validate_settings_after_logging(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    name = "test_validate_settings_after_logging"
    workspace = argilla_user.username

    await delete_dataset(async_client, name, workspace)
    await create_dataset(async_client, name, workspace)

    response = await log_some_data(async_client, name, workspace)
    assert response.status_code == 200

    response = await create_settings(async_client, name, workspace)
    assert response.status_code == 400

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "The label Mocking was found in the dataset but "
                "not in provided labels schema. \n"
                "Please, provide a valid labels schema "
                "according to stored records in the dataset"
            },
        }
    }


# TODO: These tests are the same for token an text classification. We will move them to a common test_dataset_settings
#  module where settings will be tested in a per-task fashion.
@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification])
@pytest.mark.asyncio
async def test_save_settings_as_annotator(async_client: "AsyncClient", owner_auth_header: dict, task: TaskType):
    dataset_name = "test_save_settings_as_annotator"
    workspace_name = "workspace-a"
    workspace = await WorkspaceFactory.create(name="workspace-a")
    annotator = await AnnotatorFactory.create(workspaces=[workspace])

    async_client.headers.update(owner_auth_header)

    await async_client.delete(f"/api/datasets/{dataset_name}?workspace={workspace_name}", headers=owner_auth_header)

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": task, "workspace": workspace_name},
        headers=owner_auth_header,
    )
    assert response.status_code == 200

    response = await async_client.put(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        json={"label_schema": {"labels": ["Label1", "Label2"]}},
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ForbiddenOperationError",
            "params": {"detail": "You don't have the necessary permissions to " "save settings for this dataset."},
        }
    }


@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification])
@pytest.mark.asyncio
async def test_delete_settings_as_annotator(async_client: "AsyncClient", owner_auth_header: dict, task: TaskType):
    dataset_name = "test_delete_settings_as_annotator"
    workspace_name = "workspace-a"
    workspace = await WorkspaceFactory.create(name="workspace-a")
    annotator = await AnnotatorFactory.create(workspaces=[workspace])

    await async_client.delete(f"/api/datasets/{dataset_name}?workspace={workspace_name}", headers=owner_auth_header)

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": task, "workspace": workspace_name},
        headers=owner_auth_header,
    )
    assert response.status_code == 200

    response = await async_client.delete(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ForbiddenOperationError",
            "params": {"detail": "You don't have the necessary permissions to " "delete settings for this dataset."},
        }
    }


@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification])
@pytest.mark.asyncio
async def test_get_settings_as_annotator(async_client: "AsyncClient", owner_auth_header: dict, task: TaskType):
    dataset_name = "test_get_settings_as_annotator"
    workspace_name = "workspace-a"
    workspace = await WorkspaceFactory.create(name="workspace-a")
    annotator = await AnnotatorFactory.create(workspaces=[workspace])

    await async_client.delete(f"/api/datasets/{dataset_name}?workspace={workspace_name}", headers=owner_auth_header)

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": task, "workspace": workspace_name},
        headers=owner_auth_header,
    )
    assert response.status_code == 200

    response = await async_client.put(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        json={"label_schema": {"labels": ["Label1", "Label2"]}},
        headers=owner_auth_header,
    )

    stored_settings = response.json()
    response = await async_client.get(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 200
    assert response.json() == stored_settings
