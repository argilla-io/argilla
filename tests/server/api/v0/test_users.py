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
from uuid import uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import User, UserRole
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    OwnerFactory,
    UserFactory,
    WorkspaceFactory,
    WorkspaceUserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def test_me(client: TestClient, owner, owner_auth_header):
    response = client.get("/api/me", headers=owner_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["id"] == str(owner.id)


def test_me_without_authentication(client: TestClient):
    response = client.get("/api/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_as_owner(client: TestClient):
    workspace_a = await WorkspaceFactory.create(name="workspace-a")
    workspace_b = await WorkspaceFactory.create(name="workspace-b")
    owner = await OwnerFactory.create(workspaces=[workspace_a, workspace_b])
    await WorkspaceFactory.create(name="workspace-c")

    response = client.get("/api/me", headers={API_KEY_HEADER_NAME: owner.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["id"] == str(owner.id)
    assert response_body["workspaces"] == ["workspace-a", "workspace-b", "workspace-c"]


@pytest.mark.asyncio
async def test_me_as_admin(client: TestClient):
    workspace_a = await WorkspaceFactory.create(name="workspace-a")
    workspace_b = await WorkspaceFactory.create(name="workspace-b")
    admin = await AdminFactory.create(workspaces=[workspace_a, workspace_b])
    await WorkspaceFactory.create(name="workspace-c")

    response = client.get("/api/me", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["id"] == str(admin.id)
    assert response_body["workspaces"] == ["workspace-a", "workspace-b"]


@pytest.mark.asyncio
async def test_me_as_annotator(client: TestClient, db: "AsyncSession"):
    workspace_a = await WorkspaceFactory.create(name="workspace-a")
    workspace_b = await WorkspaceFactory.create(name="workspace-b")
    annotator = await AnnotatorFactory.create(workspaces=[workspace_a, workspace_b])
    await WorkspaceFactory.create(name="workspace-c")

    response = client.get("/api/me", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["id"] == str(annotator.id)
    assert response_body["workspaces"] == ["workspace-a", "workspace-b"]


@pytest.mark.asyncio
async def test_list_users(client: TestClient, owner_auth_header: dict):
    await UserFactory.create(username="username-a")
    await UserFactory.create(username="username-b")

    response = client.get("/api/users", headers=owner_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert list(map(lambda user: user["username"], response_body)) == ["owner", "username-a", "username-b"]


def test_list_users_without_authentication(client: TestClient):
    response = client.get("/api/users")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_as_admin(client: TestClient, db: "AsyncSession"):
    admin = await AdminFactory.create()

    response = client.get("/api/users", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_users_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()

    response = client.get("/api/users", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user(client: TestClient, db: "AsyncSession", owner_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(User.id)))).scalar() == 2

    db_user = (await db.execute(select(User).where(User.username == "username"))).scalar_one_or_none()
    assert db_user

    response_body = response.json()
    assert response_body["username"] == "username"
    assert response_body["api_key"] == db_user.api_key
    assert response_body["role"] == UserRole.annotator.value


@pytest.mark.asyncio
async def test_create_user_with_non_default_role(client: TestClient, db: "AsyncSession", owner_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "12345678", "role": UserRole.owner.value}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(User.id)))).scalar() == 2

    db_user = (await db.execute(select(User).where(User.username == "username"))).scalar_one_or_none()
    assert db_user

    response_body = response.json()
    assert response_body["username"] == "username"
    assert response_body["role"] == UserRole.owner.value


@pytest.mark.asyncio
async def test_create_user_without_authentication(client: TestClient, db: "AsyncSession"):
    user = {"first_name": "first-name", "username": "username", "password": "12345678"}

    response = client.post("/api/users", json=user)

    assert response.status_code == 401
    assert (await db.execute(select(func.count(User.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_create_user_as_admin(client: TestClient, db: "AsyncSession"):
    admin = await AdminFactory.create()
    user = {"first_name": "first-name", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers={API_KEY_HEADER_NAME: admin.api_key}, json=user)

    assert response.status_code == 403
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_user_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    user = {"first_name": "first-name", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=user)

    assert response.status_code == 403
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_user_with_existent_username(client: TestClient, db: "AsyncSession", owner_auth_header: dict):
    await UserFactory.create(username="username")
    user = {"first_name": "first-name", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 409
    assert (await db.execute(select(func.count(User.id)))).scalar() == 2


@pytest.mark.asyncio
async def test_create_user_with_invalid_min_length_first_name(
    client: TestClient, db: "AsyncSession", owner_auth_header: dict
):
    user = {"first_name": "", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_user_with_invalid_min_length_last_name(client: TestClient, db: "AsyncSession", owner_auth_header):
    user = {"first_name": "first-name", "last_name": "", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_user_with_invalid_username(client: TestClient, db: "AsyncSession", owner_auth_header: dict):
    user = {"first_name": "first-name", "username": "invalid username", "password": "12345678"}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_user_with_invalid_role(client: TestClient, db: "AsyncSession", owner_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "12345678", "role": "invalid role"}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_user_with_invalid_min_password_length(
    client: TestClient, db: "AsyncSession", owner_auth_header: dict
):
    user = {"first_name": "first-name", "username": "username", "password": "1234"}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_create_user_with_invalid_max_password_length(
    client: TestClient, db: "AsyncSession", owner_auth_header: dict
):
    user = {"first_name": "first-name", "username": "username", "password": "p" * 101}

    response = client.post("/api/users", headers=owner_auth_header, json=user)

    assert response.status_code == 422
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_user(client: TestClient, db: "AsyncSession", owner_auth_header: dict):
    user = await UserFactory.create()

    response = client.delete(f"/api/users/{user.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    response_body = response.json()
    assert response_body["id"] == str(user.id)


@pytest.mark.asyncio
async def test_delete_user_without_authentication(client: TestClient, db: "AsyncSession"):
    user = await UserFactory.create()

    response = client.delete(f"/api/users/{user.id}")

    assert response.status_code == 401
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_user_as_admin(client: TestClient, db: "AsyncSession"):
    admin = await AdminFactory.create()
    user = await UserFactory.create()

    response = client.delete(f"/api/users/{user.id}", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert response.status_code == 403
    assert (await db.execute(select(func.count(User.id)))).scalar() == 2


@pytest.mark.asyncio
async def test_delete_user_as_annotator(client: TestClient, db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    user = await UserFactory.create()

    response = client.delete(f"/api/users/{user.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert (await db.execute(select(func.count(User.id)))).scalar() == 2


@pytest.mark.asyncio
async def test_delete_user_with_nonexistent_user_id(client: TestClient, db: "AsyncSession", owner_auth_header: dict):
    response = client.delete(f"/api/users/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(User.id)))).scalar() == 1
