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
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User, Workspace, WorkspaceUser
from sqlalchemy import func, select

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    UserFactory,
    WorkspaceFactory,
    WorkspaceUserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_workspace(async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict):
    response = await async_client.post("/api/workspaces", headers=owner_auth_header, json={"name": "workspace"})

    assert response.status_code == 200
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 1

    response_body = response.json()
    assert response_body["name"] == "workspace"
    assert await db.get(Workspace, UUID(response_body["id"]))


@pytest.mark.asyncio
async def test_create_workspace_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    response = await async_client.post("/api/workspaces", json={"name": "workspace"})

    assert response.status_code == 401
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_as_admin(async_client: "AsyncClient", db: "AsyncSession"):
    admin = await AdminFactory.create()

    response = await async_client.post(
        "/api/workspaces", headers={API_KEY_HEADER_NAME: admin.api_key}, json={"name": "workspaces"}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()

    response = await async_client.post(
        "/api/workspaces", headers={API_KEY_HEADER_NAME: annotator.api_key}, json={"name": "workspaces"}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_with_existent_name(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    await WorkspaceFactory.create(name="workspace")

    response = await async_client.post("/api/workspaces", headers=owner_auth_header, json={"name": "workspace"})

    assert response.status_code == 409
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_workspace_with_invalid_min_length_name(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    response = await async_client.post("/api/workspaces", headers=owner_auth_header, json={"name": ""})

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_with_invalid_name(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    response = await async_client.post("/api/workspaces", headers=owner_auth_header, json={"name": "invalid name"})

    assert response.status_code == 422
    assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
@pytest.mark.asyncio
async def test_delete_workspace():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
@pytest.mark.asyncio
async def test_delete_workspace_without_authentication():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
@pytest.mark.asyncio
async def test_delete_workspace_as_annotator():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
@pytest.mark.asyncio
async def test_delete_workspace_with_nonexistent_workspace_id():
    pass


@pytest.mark.asyncio
async def test_list_workspace_users(async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict):
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

    response = await async_client.get(f"/api/workspaces/{workspace_a.id}/users", headers=owner_auth_header)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 5

    response_body = response.json()
    assert list(map(lambda u: u["username"], response_body)) == ["username-a", "username-b", "username-c"]


@pytest.mark.asyncio
async def test_list_workspace_users_without_authentication(async_client: "AsyncClient"):
    workspace = await WorkspaceFactory.create()

    response = await async_client.get(f"/api/workspaces/{workspace.id}/users")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_workspace_users_as_admin(async_client: "AsyncClient", db: "AsyncSession"):
    admin = await AdminFactory.create()
    workspace = await WorkspaceFactory.create()
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=admin.id)

    user_a = await UserFactory.create(username="username-a")
    user_b = await UserFactory.create(username="username-b")
    user_c = await UserFactory.create(username="username-c")
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user_a.id)
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user_b.id)
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user_c.id)

    response = await async_client.get(
        f"/api/workspaces/{workspace.id}/users", headers={API_KEY_HEADER_NAME: admin.api_key}
    )

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 4

    response_body = response.json()
    assert list(map(lambda u: u["username"], response_body)) == [
        admin.username,
        "username-a",
        "username-b",
        "username-c",
    ]


@pytest.mark.asyncio
async def test_list_workspace_users_as_annotator(async_client: "AsyncClient"):
    annotator = await AnnotatorFactory.create()
    workspace = await WorkspaceFactory.create()

    response = await async_client.get(
        f"/api/workspaces/{workspace.id}/users", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_workspace_user(
    async_client: "AsyncClient", db: "AsyncSession", owner: "User", owner_auth_header: dict
):
    workspace = await WorkspaceFactory.create()

    response = await async_client.post(f"/api/workspaces/{workspace.id}/users/{owner.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1
    assert (await db.execute(select(WorkspaceUser).filter_by(workspace_id=workspace.id, user_id=owner.id))).scalar_one()

    response_body = response.json()
    assert response_body["id"] == str(owner.id)
    assert workspace.name in response_body["workspaces"]


@pytest.mark.asyncio
async def test_create_workspace_user_without_authentication(async_client: "AsyncClient", db: "AsyncSession", owner):
    workspace = await WorkspaceFactory.create()

    response = await async_client.post(f"/api/workspaces/{workspace.id}/users/{owner.id}")

    assert response.status_code == 401
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_as_admin(async_client: "AsyncClient", db: "AsyncSession"):
    admin = await AdminFactory.create()
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()

    response = await async_client.post(
        f"/api/workspaces/{workspace.id}/users/{user.id}", headers={API_KEY_HEADER_NAME: admin.api_key}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()

    response = await async_client.post(
        f"/api/workspaces/{workspace.id}/users/{user.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_with_nonexistent_workspace_id(
    async_client: "AsyncClient", db: "AsyncSession", owner: "User", owner_auth_header: dict
):
    response = await async_client.post(f"/api/workspaces/{uuid4()}/users/{owner.id}", headers=owner_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_with_nonexistent_user_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    workspace = await WorkspaceFactory.create()

    response = await async_client.post(f"/api/workspaces/{workspace.id}/users/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_workspace_user_with_existent_workspace_id_and_user_id(
    async_client: "AsyncClient", db: "AsyncSession", owner: "User", owner_auth_header: dict
):
    workspace = await WorkspaceFactory.create()
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)

    response = await async_client.post(f"/api/workspaces/{workspace.id}/users/{owner.id}", headers=owner_auth_header)

    assert response.status_code == 409
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user(async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = await async_client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}", headers=owner_auth_header
    )

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    response_body = response.json()
    assert response_body["id"] == str(workspace_user.user_id)


@pytest.mark.asyncio
async def test_delete_workspace_user_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = await async_client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}"
    )

    assert response.status_code == 401
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user_as_admin(async_client: "AsyncClient", db: "AsyncSession"):
    admin = await AdminFactory.create()
    workspace = await WorkspaceFactory.create()

    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=admin.id)
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = await async_client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}",
        headers={API_KEY_HEADER_NAME: admin.api_key},
    )

    assert response.status_code == 200
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1

    response_body = response.json()
    assert response_body["id"] == str(workspace_user.user_id)


@pytest.mark.asyncio
async def test_delete_workspace_user_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(
        workspace_id=workspace.id,
        user_id=user.id,
    )

    response = await async_client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user_with_nonexistent_workspace_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = await async_client.delete(
        f"/api/workspaces/{uuid4()}/users/{workspace_user.user_id}", headers=owner_auth_header
    )

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_workspace_user_with_nonexistent_user_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create()
    workspace_user = await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    response = await async_client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{uuid4()}", headers=owner_auth_header
    )

    assert response.status_code == 404
    assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1
