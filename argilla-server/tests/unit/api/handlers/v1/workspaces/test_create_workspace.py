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

import pytest
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import UserRole
from argilla_server.models import Workspace
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory, WorkspaceFactory


@pytest.mark.asyncio
class TestCreateWorkspace:
    def url(self) -> str:
        return "/api/v1/workspaces"

    async def test_create_workspace(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={"name": "workspace"},
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 1
        workspace = (await db.execute(select(Workspace).filter_by(name="workspace"))).scalar_one()

        assert response.json() == {
            "id": str(workspace.id),
            "name": "workspace",
            "inserted_at": workspace.inserted_at.isoformat(),
            "updated_at": workspace.updated_at.isoformat(),
        }

    async def test_create_workspace_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        response = await async_client.post(
            self.url(),
            json={"name": "workspace"},
        )

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_create_workspace_with_unauthorized_role(
        self, db: AsyncSession, async_client: AsyncClient, user_role: UserRole
    ):
        user = await UserFactory.create(role=user_role)

        response = await async_client.post(
            self.url(),
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"name": "workspace"},
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0

    async def test_create_workspace_with_existent_name(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        await WorkspaceFactory.create(name="workspace")

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={"name": "workspace"},
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "Workspace name `workspace` is not unique"}

        assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 1

    async def test_create_workspace_with_invalid_min_length_name(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={"name": ""},
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Workspace.id)))).scalar() == 0
