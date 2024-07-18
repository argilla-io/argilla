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

from tests.factories import UserFactory, WorkspaceFactory, WorkspaceUserFactory


@pytest.mark.asyncio
class TestCreateWorkspaceUser:
    def url(self, workspace_id: UUID) -> str:
        return f"/api/v1/workspaces/{workspace_id}/users"

    async def test_create_workspace_user(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create()

        response = await async_client.post(
            self.url(workspace.id),
            headers=owner_auth_header,
            json={"user_id": str(user.id)},
        )

        assert response.status_code == 201
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

        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1
        assert (
            await db.execute(
                select(WorkspaceUser).filter_by(
                    workspace_id=workspace.id, user_id=user.id
                )
            )
        ).scalar_one()

    async def test_create_workspace_user_without_authentication(
        self, db: AsyncSession, async_client: AsyncClient
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create()

        response = await async_client.post(
            self.url(workspace.id),
            json={"user_id": str(user.id)},
        )

        assert response.status_code == 401
        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_create_workspace_user_with_unauthorized_role(
        self, db: AsyncSession, async_client: AsyncClient, user_role: UserRole
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(role=user_role)

        response = await async_client.post(
            self.url(workspace.id),
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"user_id": str(user.id)},
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    async def test_create_workspace_user_with_nonexistent_workspace_id(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace_id = uuid4()
        user = await UserFactory.create()

        response = await async_client.post(
            self.url(workspace_id),
            headers=owner_auth_header,
            json={"user_id": str(user.id)},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": f"Workspace with id `{workspace_id}` not found"
        }

        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    async def test_create_workspace_user_with_nonexistent_user_id(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        user_id = uuid4()

        response = await async_client.post(
            self.url(workspace.id),
            headers=owner_auth_header,
            json={"user_id": str(user_id)},
        )

        assert response.status_code == 422
        assert response.json() == {"detail": f"User with id `{user_id}` not found"}

        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 0

    async def test_create_workspace_user_with_existent_workspace_id_and_user_id(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create()
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

        response = await async_client.post(
            self.url(workspace.id),
            headers=owner_auth_header,
            json={"user_id": str(user.id)},
        )

        assert response.status_code == 409
        assert response.json() == {
            "detail": f"Workspace user with workspace_id `{workspace.id}` and user_id `{user.id}` is not unique",
        }

        assert (await db.execute(select(func.count(WorkspaceUser.id)))).scalar() == 1
