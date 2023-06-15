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

from uuid import UUID

import pytest
from argilla._constants import DEFAULT_API_KEY
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.workspaces.api import (
    create_workspace,
    create_workspace_user,
    delete_workspace_user,
    list_workspace_users,
    list_workspaces,
)
from argilla.client.sdk.workspaces.models import WorkspaceModel, WorkspaceUserModel
from pytest import MonkeyPatch

from tests.helpers import SecuredClient


@pytest.fixture
def sdk_client() -> AuthenticatedClient:
    return AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY).httpx


def test_list_workspaces(
    mocked_client: SecuredClient, sdk_client: AuthenticatedClient, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(sdk_client, "get", mocked_client.get)

    workspace_name = "test_workspace"
    mocked_client.post(f"/api/workspaces", json={"name": workspace_name})

    response = list_workspaces(client=sdk_client)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], WorkspaceModel)


def test_create_workspace(
    mocked_client: SecuredClient, sdk_client: AuthenticatedClient, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(sdk_client, "post", mocked_client.post)

    workspace_name = "test_workspace"
    response = create_workspace(client=sdk_client, name=workspace_name)
    assert response.status_code == 200
    assert isinstance(response.parsed, WorkspaceModel)
    assert response.parsed.name == workspace_name


def test_list_workspace_users(
    mocked_client: SecuredClient, sdk_client: AuthenticatedClient, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(sdk_client, "get", mocked_client.get)

    workspace_name = "test_workspace"
    workspace = mocked_client.post(f"/api/workspaces", json={"name": workspace_name}).json()
    user_name = "test_user"
    user = mocked_client.post(
        "/api/users",
        json={
            "first_name": "string",
            "last_name": "string",
            "username": user_name,
            "role": "admin",
            "password": "stringst",
        },
    ).json()
    mocked_client.post(f"/api/workspaces/{workspace['id']}/users/{user['id']}")

    response = list_workspace_users(client=sdk_client, id=workspace["id"])
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], WorkspaceUserModel)


def test_create_workspace_user(
    mocked_client: SecuredClient, sdk_client: AuthenticatedClient, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(sdk_client, "post", mocked_client.post)

    workspace_name = "test_workspace"
    workspace = mocked_client.post(f"/api/workspaces", json={"name": workspace_name}).json()
    user_name = "test_user"
    user = mocked_client.post(
        "/api/users",
        json={
            "first_name": "string",
            "last_name": "string",
            "username": user_name,
            "role": "admin",
            "password": "stringst",
        },
    ).json()

    response = create_workspace_user(client=sdk_client, id=workspace["id"], user_id=user["id"])
    assert response.status_code == 200
    assert isinstance(response.parsed, WorkspaceUserModel)
    assert response.parsed.id == UUID(user["id"])
    assert response.parsed.workspaces[0] == workspace["name"]


def test_delete_workspace_user(
    mocked_client: SecuredClient, sdk_client: AuthenticatedClient, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(sdk_client, "delete", mocked_client.delete)

    workspace_name = "test_workspace"
    workspace = mocked_client.post(f"/api/workspaces", json={"name": workspace_name}).json()
    user_name = "test_user"
    user = mocked_client.post(
        "/api/users",
        json={
            "first_name": "string",
            "last_name": "string",
            "username": user_name,
            "role": "admin",
            "password": "stringst",
        },
    ).json()
    mocked_client.post(f"/api/workspaces/{workspace['id']}/users/{user['id']}").json()

    response = delete_workspace_user(client=sdk_client, id=workspace["id"], user_id=user["id"])
    assert response.status_code == 200
    assert response.parsed.workspaces == []
