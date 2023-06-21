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

from argilla._constants import API_KEY_HEADER_NAME
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import AnnotatorFactory, WorkspaceFactory


def test_get_workspace(client: TestClient, owner_auth_header):
    workspace = WorkspaceFactory.create(name="workspace")

    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "id": str(workspace.id),
        "name": "workspace",
        "inserted_at": workspace.inserted_at.isoformat(),
        "updated_at": workspace.updated_at.isoformat(),
    }


def test_get_workspace_without_authentication(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()

    response = client.get(f"/api/v1/workspaces/{workspace.id}")

    assert response.status_code == 401


def test_get_workspace_as_annotator(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create(name="workspace")
    annotator = AnnotatorFactory.create(workspaces=[workspace])

    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200
    assert response.json()["name"] == "workspace"


def test_get_workspace_as_annotator_from_different_workspace(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(f"/api/v1/workspaces/{workspace.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_get_workspace_with_nonexistent_workspace_id(client: TestClient, db: Session, owner_auth_header):
    WorkspaceFactory.create()

    response = client.get(f"/api/v1/workspaces/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
