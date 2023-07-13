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

from uuid import uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import UserRole
from fastapi.testclient import TestClient

from tests.factories import AnnotatorFactory, UserFactory, WorkspaceFactory


@pytest.mark.asyncio
async def test_get_workspace(client: TestClient, owner_auth_header: dict):
    workspace = await WorkspaceFactory.create(name="workspace")

    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "id": str(workspace.id),
        "name": "workspace",
        "inserted_at": workspace.inserted_at.isoformat(),
        "updated_at": workspace.updated_at.isoformat(),
    }


@pytest.mark.asyncio
async def test_get_workspace_without_authentication(client: TestClient):
    workspace = await WorkspaceFactory.create()

    response = client.get(f"/api/v1/workspaces/{workspace.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_workspace_as_annotator(client: TestClient):
    workspace = await WorkspaceFactory.create(name="workspace")
    annotator = await AnnotatorFactory.create(workspaces=[workspace])

    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200
    assert response.json()["name"] == "workspace"


@pytest.mark.asyncio
async def test_get_workspace_as_annotator_from_different_workspace(client: TestClient):
    workspace = await WorkspaceFactory.create()
    another_workspace = await WorkspaceFactory.create()
    annotator = await AnnotatorFactory.create(workspaces=[another_workspace])

    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_workspace_with_nonexistent_workspace_id(client: TestClient, owner_auth_header: dict):
    await WorkspaceFactory.create()

    response = client.get(f"/api/v1/workspaces/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
async def test_list_workspaces_me(client: TestClient, role: UserRole) -> None:
    workspaces = await WorkspaceFactory.create_batch(size=5)
    user = await UserFactory.create(role=role, workspaces=workspaces if role != UserRole.owner else [])

    response = client.get("/api/v1/me/workspaces", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200
    assert len(response.json()["items"]) == len(workspaces)
    for workspace in workspaces:
        assert {
            "id": str(workspace.id),
            "name": workspace.name,
            "inserted_at": workspace.inserted_at.isoformat(),
            "updated_at": workspace.updated_at.isoformat(),
        } in response.json()["items"]


@pytest.mark.asyncio
async def test_list_workspaces_me_without_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/me/workspaces")

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
async def test_list_workspaces_me_no_workspaces(client: TestClient, role: UserRole) -> None:
    user = await UserFactory.create(role=role)

    response = client.get("/api/v1/me/workspaces", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 0
