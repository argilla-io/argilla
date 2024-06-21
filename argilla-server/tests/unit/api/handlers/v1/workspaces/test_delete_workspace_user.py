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
from argilla_server.models import WorkspaceUser
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import AdminFactory, AnnotatorFactory, UserFactory, WorkspaceFactory, WorkspaceUserFactory


@pytest.mark.asyncio
class TestDeleteWorkspaceUser:
    def url(self, workspace_id: UUID, user_id: UUID) -> str:
        return f"/api/v1/workspaces/{workspace_id}/users/{user_id}"

    async def test_delete_workspace_user(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

        response = await async_client.delete(
            self.url(workspace.id, user.id),
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": UserRole.annotator,
            "api_key": user.api_key,
            "inserted_at": user.inserted_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    async def test_delete_workspace_user_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

        response = await async_client.delete(self.url(workspace.id, user.id))

        assert response.status_code == 401
        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1

    async def test_delete_workspace_user_as_admin(self, db: AsyncSession, async_client: AsyncClient):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=admin.id)

        response = await async_client.delete(
            self.url(workspace.id, admin.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
        )

        assert response.status_code == 200
        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    async def test_delete_workspace_user_as_admin_from_different_workspace(
        self, db: AsyncSession, async_client: AsyncClient
    ):
        workspace = await WorkspaceFactory.create()
        user = await AdminFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

        other_workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create()
        await WorkspaceUserFactory.create(workspace_id=other_workspace.id, user_id=admin.id)

        response = await async_client.delete(
            self.url(workspace.id, user.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 2

    async def test_delete_workspace_user_as_annotator(self, db: AsyncSession, async_client: AsyncClient):
        workspace = await WorkspaceFactory.create()
        annotator = await AnnotatorFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=annotator.id)

        response = await async_client.delete(
            self.url(workspace.id, annotator.id),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1

    async def test_delete_workspace_user_with_nonexistent_workspace_id(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        non_existent_workspace_id = uuid4()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

        response = await async_client.delete(
            self.url(non_existent_workspace_id, user.id),
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": f"WorkspaceUser not found filtering by workspace_id={non_existent_workspace_id}, user_id={user.id}",
        }

        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1

    async def test_delete_workspace_user_with_nonexistent_user_id(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        non_existent_user_id = uuid4()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

        response = await async_client.delete(
            self.url(workspace.id, non_existent_user_id),
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": f"WorkspaceUser not found filtering by workspace_id={workspace.id}, user_id={non_existent_user_id}",
        }

        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1
