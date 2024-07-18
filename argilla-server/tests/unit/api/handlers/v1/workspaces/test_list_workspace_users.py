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
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import UserRole
from httpx import AsyncClient

from tests.factories import AdminFactory, AnnotatorFactory, UserFactory, WorkspaceFactory, WorkspaceUserFactory


@pytest.mark.asyncio
class TestListWorkspaceUsers:
    def url(self, workspace_id: UUID) -> str:
        return f"/api/v1/workspaces/{workspace_id}/users"

    async def test_list_workspace_users(self, async_client: AsyncClient, owner_auth_header: dict):
        workspace = await WorkspaceFactory.create()
        users = await UserFactory.create_batch(3)
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=users[0].id)
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=users[1].id)
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=users[2].id)

        other_workspace = await WorkspaceFactory.create()
        other_users = await UserFactory.create_batch(2)
        await WorkspaceUserFactory.create(workspace_id=other_workspace.id, user_id=other_users[0].id)
        await WorkspaceUserFactory.create(workspace_id=other_workspace.id, user_id=other_users[1].id)

        response = await async_client.get(self.url(workspace.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(users[0].id),
                    "first_name": users[0].first_name,
                    "last_name": users[0].last_name,
                    "username": users[0].username,
                    "role": UserRole.annotator,
                    "api_key": users[0].api_key,
                    "inserted_at": users[0].inserted_at.isoformat(),
                    "updated_at": users[0].updated_at.isoformat(),
                },
                {
                    "id": str(users[1].id),
                    "first_name": users[1].first_name,
                    "last_name": users[1].last_name,
                    "username": users[1].username,
                    "role": UserRole.annotator,
                    "api_key": users[1].api_key,
                    "inserted_at": users[1].inserted_at.isoformat(),
                    "updated_at": users[1].updated_at.isoformat(),
                },
                {
                    "id": str(users[2].id),
                    "first_name": users[2].first_name,
                    "last_name": users[2].last_name,
                    "username": users[2].username,
                    "role": UserRole.annotator,
                    "api_key": users[2].api_key,
                    "inserted_at": users[2].inserted_at.isoformat(),
                    "updated_at": users[2].updated_at.isoformat(),
                },
            ],
        }

    async def test_list_workspace_users_without_authentication(self, async_client: AsyncClient):
        workspace = await WorkspaceFactory.create()

        response = await async_client.get(self.url(workspace.id))

        assert response.status_code == 401

    async def test_list_workspace_users_as_admin(self, async_client: AsyncClient):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=admin.id)

        response = await async_client.get(
            self.url(workspace.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
        )

        assert response.status_code == 200

    async def test_list_workspace_users_as_admin_from_different_workspace(self, async_client: AsyncClient):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create()

        response = await async_client.get(
            self.url(workspace.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
        )

        assert response.status_code == 403

    async def test_list_workspace_users_as_annotator(self, async_client: AsyncClient):
        workspace = await WorkspaceFactory.create()
        annotator = await AnnotatorFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=annotator.id)

        response = await async_client.get(
            self.url(workspace.id),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
        )

        assert response.status_code == 403

    async def test_list_workspace_with_nonexistent_workspace_id(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace_id = uuid4()

        response = await async_client.get(self.url(workspace_id), headers=owner_auth_header)

        assert response.status_code == 404
        assert response.json() == {"detail": f"Workspace with id `{workspace_id}` not found"}
