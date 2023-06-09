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

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import User, Workspace, WorkspaceUser
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from tests.factories import (
    AnnotatorFactory,
    UserFactory,
    WorkspaceFactory,
    WorkspaceUserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_workspaces(client: TestClient, admin_auth_header: dict):
    await WorkspaceFactory.create(name="workspace-a")
    await WorkspaceFactory.create(name="workspace-b")

    response = client.get("/api/workspaces", headers=admin_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert list(map(lambda ws: ws["name"], response_body)) == ["workspace-a", "workspace-b"]


def test_list_workspaces_without_authentication(client: TestClient):
    response = client.get("/api/workspaces")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_workspaces_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()

    response = client.get("/api/workspaces", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_workspace(client: TestClient, db: "AsyncSession", admin_auth_header: dict):
    response = client.post("/api/workspaces", headers=admin_auth_header, json={"name": "workspace"})

    assert response.status_code == 200
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 1

    response_body = response.json()
    assert response_body["name"] == "workspace"
    assert await db.get(Workspace, UUID(response_body["id"]))


@pytest.mark.asyncio
async def test_create_workspace_without_authentication(client: TestClient, db: "AsyncSession"):
    response = client.post("/api/workspaces", json={"name": "workspace"})

    assert response.status_code == 401
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()

    response = client.post(
        "/api/workspaces", headers={API_KEY_HEADER_NAME: annotator.api_key}, json={"name": "workspaces"}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_with_existent_name(client: TestClient, db: "AsyncSession", admin_auth_header: dict):
    await WorkspaceFactory.create(name="workspace")

    response = client.post("/api/workspaces", headers=admin_auth_header, json={"name": "workspace"})

    assert response.status_code == 409
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_workspace_with_invalid_min_length_name(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict
):
    response = client.post("/api/workspaces", headers=admin_auth_header, json={"name": ""})

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_with_invalid_name(client: TestClient, db: "AsyncSession", admin_auth_header: dict):
    response = client.post("/api/workspaces", headers=admin_auth_header, json={"name": "invalid name"})

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
def test_delete_workspace():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
def test_delete_workspace_without_authentication():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
def test_delete_workspace_as_annotator():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
def test_delete_workspace_with_nonexistent_workspace_id():
    pass


@pytest.mark.asyncio
async def test_list_workspace_users(client: TestClient, db: "AsyncSession", admin_auth_header: dict):
    workspace_a = await WorkspaceFactory.create()
    user_a = await UserFactory.create(username="username-a")
    user_b = await UserFactory.create(username="username-b")
    user_c = await UserFactory.create(username="username-c")
    await WorkspaceUserFactory.create(workspace_id=workspace_a.id, user_id=user_a.id)
    await WorkspaceUserFactory.create(workspace_id=workspace_a.id, user_id=user_b.id)
    await WorkspaceUserFactory.create(workspace_id=workspace_a.id, user_id=user_c.id)

    user_d = await UserFactory.create(username="username-d")
    user_e = await UserFactory.create(username="username-e")
    await WorkspaceFactory.create(users=[user_d, user_e])

    response = client.get(f"/api/workspaces/{workspace_a.id}/users", headers=admin_auth_header)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 5

    response_body = response.json()
    assert list(map(lambda u: u["username"], response_body)) == ["username-a", "username-b", "username-c"]


@pytest.mark.asyncio
async def test_list_workspace_users_without_authentication(client: TestClient):
    workspace = await WorkspaceFactory.create()

    response = client.get(f"/api/workspaces/{workspace.id}/users")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_workspace_users_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    workspace = await WorkspaceFactory.create()

    response = client.get(f"/api/workspaces/{workspace.id}/users", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_workspace_user(client: TestClient, db: "AsyncSession", admin: User, admin_auth_header: dict):
    workspace = await WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{admin.id}", headers=admin_auth_header)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1
    assert (await db.execute(select(WorkspaceUser).filter_by(workspace_id=workspace.id, user_id=admin.id))).scalar()

    response_body = response.json()
    assert response_body["id"] == str(admin.id)
    assert workspace.name in response_body["workspaces"]


@pytest.mark.asyncio
async def test_create_workspace_user_without_authentication(client: TestClient, db: "AsyncSession", admin: User):
    workspace = await WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{admin.id}")

    assert response.status_code == 401
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()

    response = client.post(
        f"/api/workspaces/{workspace.id}/users/{user.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_with_nonexistent_workspace_id(
    client: TestClient, db: "AsyncSession", admin: User, admin_auth_header: dict
):
    response = client.post(f"/api/workspaces/{uuid4()}/users/{admin.id}", headers=admin_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_with_nonexistent_user_id(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict
):
    workspace = await WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_with_existent_workspace_id_and_user_id(
    client: TestClient, db: "AsyncSession", admin: User, admin_auth_header: dict
):
    workspace = await WorkspaceFactory.create()
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=admin.id)

    response = client.post(f"/api/workspaces/{workspace.id}/users/{admin.id}", headers=admin_auth_header)

    assert response.status_code == 409
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user(client: TestClient, db: "AsyncSession", admin_auth_header: dict):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}", headers=admin_auth_header
    )

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    response_body = response.json()
    assert response_body["id"] == str(workspace_user.user_id)


@pytest.mark.asyncio
async def test_delete_workspace_user_without_authentication(client: TestClient, db: "AsyncSession"):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = client.delete(f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}")

    assert response.status_code == 401
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user_with_nonexistent_workspace_id(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict
):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = client.delete(f"/api/workspaces/{uuid4()}/users/{workspace_user.user_id}", headers=admin_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user_with_nonexistent_user_id(
    client: TestClient, db: "AsyncSession", admin_auth_header: dict
):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{uuid4()}", headers=admin_auth_header
    )

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1
