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
from typing import TYPE_CHECKING, Optional

import pytest
from argilla_server.commons.models import TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User

if TYPE_CHECKING:
    from httpx import AsyncClient


async def create_dataset(client: "AsyncClient", name: str, workspace_name: str):
    response = await client.post(
        "/api/datasets", json={"name": name, "workspace": workspace_name, f"task": TaskType.token_classification}
    )
    assert response.status_code == 200


async def delete_dataset(client: "AsyncClient", name: str, workspace_name: str):
    response = await client.delete(f"/api/datasets/{name}", params={"workspace": workspace_name})
    assert response.status_code == 200


async def create_settings(async_client: "AsyncClient", name: str, workspace_name: str, labels: Optional[list] = None):
    response = await async_client.put(
        f"/api/datasets/{TaskType.token_classification}/{name}/settings",
        json={"label_schema": {"labels": labels or ["Label1", "Label2"]}},
        params={"workspace": workspace_name},
    )
    return response


async def fetch_settings(async_client: "AsyncClient", name: str, workspace_name: str):
    return await async_client.get(
        f"/api/datasets/{TaskType.token_classification}/{name}/settings", params={"workspace": workspace_name}
    )


async def delete_dataset_settings(async_client: "AsyncClient", name: str, workspace_name: str):
    response = await async_client.delete(
        f"/api/datasets/{TaskType.token_classification}/{name}/settings", params={"workspace": workspace_name}
    )
    assert response.status_code == 200


async def log_some_data(async_client: "AsyncClient", name: str, workspace_name: str):
    response = await async_client.post(
        f"/api/datasets/{name}/TokenClassification:bulk",
        json={
            "records": [
                {
                    "tokens": "This is a text".split(" "),
                    "raw_text": "This is a text",
                    "prediction": {
                        "agent": "test",
                        "entities": [{"start": 0, "end": 4, "label": "BAD"}],
                    },
                    "annotation": {
                        "agent": "test",
                        "entities": [{"start": 0, "end": 4, "label": "BAD"}],
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

    response = await create_settings(async_client, name, workspace_name=workspace_name, labels=labels)
    assert response.status_code == 200

    created = response.json()
    response = await fetch_settings(async_client, name, workspace_name=workspace_name)
    assert response.json() == created


@pytest.mark.asyncio
async def test_get_dataset_settings_not_found(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_name = argilla_user.username

    name = "test_get_dataset_settings_not_found"
    await delete_dataset(async_client, name, workspace_name=workspace_name)
    await create_dataset(async_client, name, workspace_name=workspace_name)

    response = await fetch_settings(async_client, name, workspace_name=workspace_name)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_settings(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_name = argilla_user.username

    name = "test_delete_settings"
    await delete_dataset(async_client, name, workspace_name=workspace_name)
    await create_dataset(async_client, name, workspace_name=workspace_name)

    response = await create_settings(async_client, name, workspace_name)
    assert response.status_code == 200

    await delete_dataset_settings(async_client, name, workspace_name)

    response = await fetch_settings(async_client, name, workspace_name)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validate_settings_when_logging_data(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_name = argilla_user.username

    name = "test_validate_settings_when_logging_data"
    await delete_dataset(async_client, name, workspace_name=workspace_name)
    await create_dataset(async_client, name, workspace_name=workspace_name)

    response = await create_settings(async_client, name, workspace_name)
    assert response.status_code == 200

    response = await log_some_data(async_client, name, workspace_name)
    assert response.status_code == 400

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "Provided records contain the BAD label, "
                "that is not included in the labels schema.\n"
                "Please, annotate your records using labels "
                "defined in the labels schema."
            },
        }
    }


@pytest.mark.asyncio
async def test_validate_settings_after_logging(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_name = argilla_user.username

    name = "test_validate_settings_after_logging"
    await delete_dataset(async_client, name, workspace_name=workspace_name)
    await create_dataset(async_client, name, workspace_name=workspace_name)

    response = await log_some_data(async_client, name, workspace_name)
    assert response.status_code == 200

    response = await create_settings(async_client, name, workspace_name)
    assert response.status_code == 400

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "The label BAD was found in the dataset but "
                "not in provided labels schema. \n"
                "Please, provide a valid labels schema "
                "according to stored records in the "
                "dataset"
            },
        }
    }
