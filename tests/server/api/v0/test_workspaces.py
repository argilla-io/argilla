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
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import User, Workspace, WorkspaceUser
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    UserFactory,
    WorkspaceFactory,
    WorkspaceUserFactory,
)


def test_list_workspaces(client: TestClient, owner_auth_header):
    WorkspaceFactory.create(name="workspace-a")
    WorkspaceFactory.create(name="workspace-b")

    response = client.get("/api/workspaces", headers=owner_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert list(map(lambda ws: ws["name"], response_body)) == ["workspace-a", "workspace-b"]


def test_list_workspaces_without_authentication(client: TestClient):
    response = client.get("/api/workspaces")

    assert response.status_code == 401


def test_list_workspaces_as_admin(client: TestClient, db: Session):
    admin = AdminFactory.create()

    response = client.get("/api/workspaces", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert response.status_code == 200


def test_list_workspaces_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()

    response = client.get("/api/workspaces", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200


def test_create_workspace(client: TestClient, db: Session, owner_auth_header):
    response = client.post("/api/workspaces", headers=owner_auth_header, json={"name": "workspace"})

    assert response.status_code == 200
    assert db.query(Workspace).count() == 1

    response_body = response.json()
    assert response_body["name"] == "workspace"
    assert db.get(Workspace, UUID(response_body["id"]))


def test_create_workspace_without_authentication(client: TestClient, db: Session):
    response = client.post("/api/workspaces", json={"name": "workspace"})

    assert response.status_code == 401
    assert db.query(Workspace).count() == 0


def test_create_workspace_as_admin(client: TestClient, db: Session):
    admin = AdminFactory.create()

    response = client.post("/api/workspaces", headers={API_KEY_HEADER_NAME: admin.api_key}, json={"name": "workspaces"})

    assert response.status_code == 403
    assert db.query(Workspace).count() == 0


def test_create_workspace_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()

    response = client.post(
        "/api/workspaces", headers={API_KEY_HEADER_NAME: annotator.api_key}, json={"name": "workspaces"}
    )

    assert response.status_code == 403
    assert db.query(Workspace).count() == 0


def test_create_workspace_with_existent_name(client: TestClient, db: Session, owner_auth_header):
    WorkspaceFactory.create(name="workspace")

    response = client.post("/api/workspaces", headers=owner_auth_header, json={"name": "workspace"})

    assert response.status_code == 409
    assert db.query(Workspace).count() == 1


def test_create_workspace_with_invalid_min_length_name(client: TestClient, db: Session, owner_auth_header):
    response = client.post("/api/workspaces", headers=owner_auth_header, json={"name": ""})

    assert response.status_code == 422
    assert db.query(Workspace).count() == 0


def test_create_workspace_with_invalid_name(client: TestClient, db: Session, owner_auth_header):
    response = client.post("/api/workspaces", headers=owner_auth_header, json={"name": "invalid name"})

    assert response.status_code == 422
    assert db.query(Workspace).count() == 0


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


def test_list_workspace_users(client: TestClient, db: Session, owner_auth_header):
    workspace_a = WorkspaceFactory.create()
    WorkspaceUserFactory.create(workspace_id=workspace_a.id, user_id=UserFactory.create(username="username-a").id)
    WorkspaceUserFactory.create(workspace_id=workspace_a.id, user_id=UserFactory.create(username="username-b").id)
    WorkspaceUserFactory.create(workspace_id=workspace_a.id, user_id=UserFactory.create(username="username-c").id)

    WorkspaceFactory.create(users=[UserFactory.build(), UserFactory.build()])

    response = client.get(f"/api/workspaces/{workspace_a.id}/users", headers=owner_auth_header)

    assert response.status_code == 200
    assert db.query(WorkspaceUser).count() == 5

    response_body = response.json()
    assert list(map(lambda u: u["username"], response_body)) == ["username-a", "username-b", "username-c"]


def test_list_workspace_users_without_authentication(client: TestClient):
    workspace = WorkspaceFactory.create()

    response = client.get(f"/api/workspaces/{workspace.id}/users")

    assert response.status_code == 401


def test_list_workspace_users_as_admin(client: TestClient, db: Session):
    admin = AdminFactory.create()
    workspace = WorkspaceFactory.create()
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=admin.id)

    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=UserFactory.create(username="username-a").id)
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=UserFactory.create(username="username-b").id)
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=UserFactory.create(username="username-c").id)

    response = client.get(f"/api/workspaces/{workspace.id}/users", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert response.status_code == 200
    assert db.query(WorkspaceUser).count() == 4

    response_body = response.json()
    assert list(map(lambda u: u["username"], response_body)) == [
        admin.username,
        "username-a",
        "username-b",
        "username-c",
    ]


def test_list_workspace_users_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    workspace = WorkspaceFactory.create()

    response = client.get(f"/api/workspaces/{workspace.id}/users", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_create_workspace_user(client: TestClient, db: Session, owner, owner_auth_header):
    workspace = WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{owner.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert db.query(WorkspaceUser).count() == 1
    assert db.query(WorkspaceUser).filter_by(workspace_id=workspace.id, user_id=owner.id).first()

    response_body = response.json()
    assert response_body["id"] == str(owner.id)
    assert workspace.name in response_body["workspaces"]


def test_create_workspace_user_without_authentication(client: TestClient, db: Session, owner):
    workspace = WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{owner.id}")

    assert response.status_code == 401
    assert db.query(WorkspaceUser).count() == 0


def test_create_workspace_user_as_admin(client: TestClient, db: Session):
    admin = AdminFactory.create()
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()

    response = client.post(
        f"/api/workspaces/{workspace.id}/users/{user.id}", headers={API_KEY_HEADER_NAME: admin.api_key}
    )

    assert response.status_code == 403
    assert db.query(WorkspaceUser).count() == 0


def test_create_workspace_user_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()

    response = client.post(
        f"/api/workspaces/{workspace.id}/users/{user.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403
    assert db.query(WorkspaceUser).count() == 0


def test_create_workspace_user_with_nonexistent_workspace_id(client: TestClient, db: Session, owner, owner_auth_header):
    response = client.post(f"/api/workspaces/{uuid4()}/users/{owner.id}", headers=owner_auth_header)

    assert response.status_code == 404
    assert db.query(WorkspaceUser).count() == 0


def test_create_workspace_user_with_nonexistent_user_id(client: TestClient, db: Session, owner_auth_header):
    workspace = WorkspaceFactory.create()

    response = client.post(f"/api/workspaces/{workspace.id}/users/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert db.query(WorkspaceUser).count() == 0


def test_create_workspace_user_with_existent_workspace_id_and_user_id(
    client: TestClient, db: Session, owner, owner_auth_header
):
    workspace = WorkspaceFactory.create()
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)

    response = client.post(f"/api/workspaces/{workspace.id}/users/{owner.id}", headers=owner_auth_header)

    assert response.status_code == 409
    assert db.query(WorkspaceUser).count() == 1


def test_delete_workspace_user(client: TestClient, db: Session, owner_auth_header):
    workspace_user = WorkspaceUserFactory.create(
        workspace_id=WorkspaceFactory.create().id,
        user_id=UserFactory.create().id,
    )

    response = client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}", headers=owner_auth_header
    )

    assert response.status_code == 200
    assert db.query(WorkspaceUser).count() == 0

    response_body = response.json()
    assert response_body["id"] == str(workspace_user.user_id)


def test_delete_workspace_user_without_authentication(client: TestClient, db: Session):
    workspace_user = WorkspaceUserFactory.create(
        workspace_id=WorkspaceFactory.create().id,
        user_id=UserFactory.create().id,
    )

    response = client.delete(f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}")

    assert response.status_code == 401
    assert db.query(WorkspaceUser).count() == 1


def test_delete_workspace_user_as_admin(client: TestClient, db: Session):
    admin = AdminFactory.create()
    workspace = WorkspaceFactory.create()

    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=admin.id)
    workspace_user = WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=UserFactory.create().id)

    response = client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}",
        headers={API_KEY_HEADER_NAME: admin.api_key},
    )

    assert response.status_code == 200
    assert db.query(WorkspaceUser).count() == 1

    response_body = response.json()
    assert response_body["id"] == str(workspace_user.user_id)


def test_delete_workspace_user_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    workspace_user = WorkspaceUserFactory.create(
        workspace_id=WorkspaceFactory.create().id,
        user_id=UserFactory.create().id,
    )

    response = client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{workspace_user.user_id}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert db.query(WorkspaceUser).count() == 1


def test_delete_workspace_user_with_nonexistent_workspace_id(client: TestClient, db: Session, owner_auth_header):
    workspace_user = WorkspaceUserFactory.create(
        workspace_id=WorkspaceFactory.create().id, user_id=UserFactory.create().id
    )

    response = client.delete(f"/api/workspaces/{uuid4()}/users/{workspace_user.user_id}", headers=owner_auth_header)

    assert response.status_code == 404
    assert db.query(WorkspaceUser).count() == 1


def test_delete_workspace_user_with_nonexistent_user_id(client: TestClient, db: Session, owner_auth_header):
    workspace_user = WorkspaceUserFactory.create(
        workspace_id=WorkspaceFactory.create().id,
        user_id=UserFactory.create().id,
    )

    response = client.delete(
        f"/api/workspaces/{workspace_user.workspace_id}/users/{uuid4()}", headers=owner_auth_header
    )

    assert response.status_code == 404
    assert db.query(WorkspaceUser).count() == 1
