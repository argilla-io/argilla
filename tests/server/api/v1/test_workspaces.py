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
import contextlib
from uuid import uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.commons.models import TaskType
from argilla.server.models import UserRole
from fastapi.testclient import TestClient

from tests.factories import (
    DatasetFactory,
)


@contextlib.contextmanager
def create_old_argilla_dataset(client: TestClient, name: str, workspace_name: str, task: TaskType):
    try:
        response = client.post("/api/datasets", json={"name": name, "workspace": workspace_name, "task": task.value})
        assert response.status_code == 200

        yield response.json()
    finally:
        response = client.delete(f"/api/datasets/{name}?workspace={workspace_name}")
        assert response.status_code == 200


from tests.factories import AnnotatorFactory, UserFactory, WorkspaceFactory


@pytest.mark.asyncio
class TestSuiteWorkspaces:
    async def test_get_workspace(self, client: TestClient, owner_auth_header: dict):
        workspace = await WorkspaceFactory.create(name="workspace")

        response = client.get(f"/api/v1/workspaces/{workspace.id}", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(workspace.id),
            "name": "workspace",
            "inserted_at": workspace.inserted_at.isoformat(),
            "updated_at": workspace.updated_at.isoformat(),
        }

    async def test_get_workspace_without_authentication(self, client: TestClient):
        workspace = await WorkspaceFactory.create()

        response = client.get(f"/api/v1/workspaces/{workspace.id}")

        assert response.status_code == 401

    async def test_get_workspace_as_annotator(self, client: TestClient):
        workspace = await WorkspaceFactory.create(name="workspace")
        annotator = await AnnotatorFactory.create(workspaces=[workspace])

        response = client.get(f"/api/v1/workspaces/{workspace.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

        assert response.status_code == 200
        assert response.json()["name"] == "workspace"

    async def test_get_workspace_as_annotator_from_different_workspace(self, client: TestClient):
        workspace = await WorkspaceFactory.create()
        another_workspace = await WorkspaceFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[another_workspace])

        response = client.get(f"/api/v1/workspaces/{workspace.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

        assert response.status_code == 403

    async def test_get_workspace_with_nonexistent_workspace_id(self, client: TestClient, owner_auth_header: dict):
        await WorkspaceFactory.create()

        response = client.get(f"/api/v1/workspaces/{uuid4()}", headers=owner_auth_header)

        assert response.status_code == 404

    async def test_delete_workspace(self, client: TestClient, owner_auth_header: dict):
        workspace = await WorkspaceFactory.create(name="workspace_delete")
        other_workspace = await WorkspaceFactory.create()

        await DatasetFactory.create_batch(3, workspace=other_workspace)

        response = client.delete(f"/api/v1/workspaces/{workspace.id}", headers=owner_auth_header)

        assert response.status_code == 200

    async def test_delete_workspace_with_feedback_datasets(self, client: TestClient, owner_auth_header: dict):
        workspace = await WorkspaceFactory.create(name="workspace_delete")

        await DatasetFactory.create_batch(3, workspace=workspace)

        response = client.delete(f"/api/v1/workspaces/{workspace.id}", headers=owner_auth_header)

        assert response.status_code == 409
        assert response.json() == {
            "detail": f"Cannot delete the workspace {workspace.id}. This workspace has some feedback datasets linked"
        }

    @pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification, TaskType.text2text])
    async def test_delete_workspace_with_old_datasets(
        self, client: TestClient, owner_auth_header: dict, task: TaskType
    ):
        workspace = await WorkspaceFactory.create(name="workspace_delete")

        client.headers.update(owner_auth_header)
        with create_old_argilla_dataset(client, name="dataset", workspace_name=workspace.name, task=task):
            response = client.delete(f"/api/v1/workspaces/{workspace.id}")

            assert response.status_code == 409
            assert response.json() == {
                "detail": f"Cannot delete the workspace {workspace.id}. This workspace has some datasets linked"
            }

    async def test_delete_missing_workspace(self, client: TestClient, owner_auth_header: dict):
        client.headers.update(owner_auth_header)
        response = client.delete(f"/api/v1/workspaces/{uuid4()}")

        assert response.status_code == 404

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_delete_workspace_without_permissions(self, client: TestClient, role: UserRole):
        workspace = await WorkspaceFactory.create(name="workspace_delete")

        user = await UserFactory.create(role=role, workspaces=[workspace])
        client.headers.update({API_KEY_HEADER_NAME: user.api_key})
        response = client.delete(f"/api/v1/workspaces/{workspace.id}")

        assert response.status_code == 403

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

    async def test_list_workspaces_me_without_authentication(client: TestClient) -> None:
        response = client.get("/api/v1/me/workspaces")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
    async def test_list_workspaces_me_no_workspaces(client: TestClient, role: UserRole) -> None:
        user = await UserFactory.create(role=role)

        response = client.get("/api/v1/me/workspaces", headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 200
        assert len(response.json()["items"]) == 0
