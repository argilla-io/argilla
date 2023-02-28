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

from uuid import UUID, uuid4

import pytest
from argilla.server.models import User, UserWorkspace, Workspace
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import UserFactory, UserWorkspaceFactory, WorkspaceFactory


def test_list_workspaces(client: TestClient, admin_auth_header: dict):
    WorkspaceFactory.create(name="workspace-a")
    WorkspaceFactory.create(name="workspace-b")

    response = client.get("/api/workspaces", headers=admin_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert list(map(lambda ws: ws["name"], response_body)) == ["workspace-a", "workspace-b"]


def test_list_workspaces_without_authentication(client: TestClient):
    response = client.get("/api/workspaces")

    assert response.status_code == 401


def test_create_workspace(client: TestClient, db: Session, admin_auth_header: dict):
    response = client.post("/api/workspaces", headers=admin_auth_header, json={"name": "workspace"})

    assert response.status_code == 200
    assert db.query(Workspace).count() == 1

    response_body = response.json()
    assert response_body["name"] == "workspace"
    assert db.get(Workspace, UUID(response_body["id"]))


def test_create_workspace_without_authentication(client: TestClient, db: Session):
    response = client.post("/api/workspaces", json={"name": "workspace"})

    assert response.status_code == 401
    assert db.query(Workspace).count() == 0


def test_create_workspace_with_empty_name(client: TestClient, db: Session, admin_auth_header: dict):
    response = client.post("/api/workspaces", headers=admin_auth_header, json={"name": ""})

    assert response.status_code == 422
    assert db.query(Workspace).count() == 0


def test_create_workspace_with_invalid_name(client: TestClient, db: Session, admin_auth_header: dict):
    response = client.post("/api/workspaces", headers=admin_auth_header, json={"name": "invalid name"})

    assert response.status_code == 422
    assert db.query(Workspace).count() == 0


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
def test_delete_workspace():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
def test_delete_workspace_without_authentication():
    pass


@pytest.mark.skip(reason="we are not allowing deletion of workspaces right now")
def test_delete_workspace_with_nonexistent_workspace_id():
    pass


def test_list_workspace_users(client: TestClient, db: Session, admin_auth_header: dict):
    workspace_a = WorkspaceFactory.create()
    UserWorkspaceFactory.create(user_id=UserFactory.create(username="username-a").id, workspace_id=workspace_a.id)
    UserWorkspaceFactory.create(user_id=UserFactory.create(username="username-b").id, workspace_id=workspace_a.id)
    UserWorkspaceFactory.create(user_id=UserFactory.create(username="username-c").id, workspace_id=workspace_a.id)

    WorkspaceFactory.create(users=[UserFactory.build(), UserFactory.build()])

    response = client.get(f"/api/workspaces/{workspace_a.id}/users", headers=admin_auth_header)

    assert response.status_code == 200
    assert db.query(UserWorkspace).count() == 5

    response_body = response.json()
    assert list(map(lambda u: u["username"], response_body)) == ["username-a", "username-b", "username-c"]


def test_list_workspace_users_without_authentication(client: TestClient):
    workspace = WorkspaceFactory.create()

    response = client.get(f"/api/workspaces/{workspace.id}/users")

    assert response.status_code == 401


def test_create_workspace_user(client: TestClient, db: Session, admin: User, admin_auth_header: dict):
    workspace = WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{admin.id}", headers=admin_auth_header)

    assert response.status_code == 200
    assert db.query(UserWorkspace).count() == 1
    assert db.query(UserWorkspace).filter_by(user_id=admin.id, workspace_id=workspace.id).first()

    response_body = response.json()
    assert response_body["id"] == str(admin.id)
    assert workspace.name in response_body["workspaces"]


def test_create_workspace_user_without_authentication(client: TestClient, db: Session, admin: User):
    workspace = WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{admin.id}")

    assert response.status_code == 401
    assert db.query(UserWorkspace).count() == 0


def test_create_workspace_user_with_nonexistent_workspace_id(
    client: TestClient, db: Session, admin: User, admin_auth_header: dict
):
    response = client.post(f"/api/workspaces/{uuid4()}/users/{admin.id}", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.query(UserWorkspace).count() == 0


def test_create_workspace_user_with_nonexistent_user_id(client: TestClient, db: Session, admin_auth_header: dict):
    workspace = WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.query(UserWorkspace).count() == 0


def test_delete_workspace_user(client: TestClient, db: Session, admin_auth_header: dict):
    user_workspace = UserWorkspaceFactory.create(
        user_id=UserFactory.create().id, workspace_id=WorkspaceFactory.create().id
    )

    response = client.delete(
        f"/api/workspaces/{user_workspace.workspace_id}/users/{user_workspace.user_id}", headers=admin_auth_header
    )

    assert response.status_code == 200
    assert db.query(UserWorkspace).count() == 0

    response_body = response.json()
    assert response_body["id"] == str(user_workspace.user_id)


def test_delete_workspace_user_without_authentication(client: TestClient, db: Session):
    user_workspace = UserWorkspaceFactory.create(
        user_id=UserFactory.create().id, workspace_id=WorkspaceFactory.create().id
    )

    response = client.delete(f"/api/workspaces/{user_workspace.workspace_id}/users/{user_workspace.user_id}")

    assert response.status_code == 401
    assert db.query(UserWorkspace).count() == 1


def test_delete_workspace_user_with_nonexistent_workspace_id(client: TestClient, db: Session, admin_auth_header: dict):
    user_workspace = UserWorkspaceFactory.create(
        user_id=UserFactory.create().id, workspace_id=WorkspaceFactory.create().id
    )

    response = client.delete(f"/api/workspaces/{uuid4()}/users/{user_workspace.user_id}", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.query(UserWorkspace).count() == 1


def test_delete_workspace_user_with_nonexistent_user_id(client: TestClient, db: Session, admin_auth_header: dict):
    user_workspace = UserWorkspaceFactory.create(
        user_id=UserFactory.create().id, workspace_id=WorkspaceFactory.create().id
    )

    response = client.delete(
        f"/api/workspaces/{user_workspace.workspace_id}/users/{uuid4()}", headers=admin_auth_header
    )

    assert response.status_code == 404
    assert db.query(UserWorkspace).count() == 1
