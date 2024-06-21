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
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import UserRole

from tests.factories import UserFactory, WorkspaceFactory

if TYPE_CHECKING:
    pass


@pytest.mark.asyncio
class TestsUsersV1Endpoints:
    async def test_list_user_workspaces(self, async_client: "AsyncClient", owner_auth_header: dict):
        workspaces = await WorkspaceFactory.create_batch(3)
        user = await UserFactory.create(workspaces=workspaces)

        response = await async_client.get(f"/api/v1/users/{user.id}/workspaces", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(workspace.id),
                    "name": workspace.name,
                    "inserted_at": workspace.inserted_at.isoformat(),
                    "updated_at": workspace.updated_at.isoformat(),
                }
                for workspace in workspaces
            ]
        }

    async def test_list_user_workspaces_for_owner(self, async_client: "AsyncClient"):
        workspaces = await WorkspaceFactory.create_batch(5)
        owner = await UserFactory.create(role=UserRole.owner)

        response = await async_client.get(
            f"/api/v1/users/{owner.id}/workspaces", headers={API_KEY_HEADER_NAME: owner.api_key}
        )
        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(workspace.id),
                    "name": workspace.name,
                    "inserted_at": workspace.inserted_at.isoformat(),
                    "updated_at": workspace.updated_at.isoformat(),
                }
                for workspace in workspaces
            ]
        }

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_user_workspaces_as_restricted_user(self, async_client: "AsyncClient", role: UserRole):
        workspaces = await WorkspaceFactory.create_batch(3)
        user = await UserFactory.create(workspaces=workspaces)
        requesting_user = await UserFactory.create(role=role)

        response = await async_client.get(
            f"/api/v1/users/{user.id}/workspaces", headers={API_KEY_HEADER_NAME: requesting_user.api_key}
        )

        assert response.status_code == 403

    async def test_list_user_workspaces_for_non_existing_user(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        user_id = uuid4()

        response = await async_client.get(
            f"/api/v1/users/{user_id}/workspaces",
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"User with id `{user_id}` not found"}
