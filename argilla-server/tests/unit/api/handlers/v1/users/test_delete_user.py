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
from argilla_server.models import User
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


@pytest.mark.asyncio
class TestDeleteUser:
    def url(self, user_id: UUID) -> str:
        return f"/api/v1/users/{user_id}"

    async def test_delete_user(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        user = await UserFactory.create()

        response = await async_client.delete(self.url(user.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": user.role,
            "api_key": user.api_key,
            "inserted_at": user.inserted_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    async def test_delete_user_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        user = await UserFactory.create()

        response = await async_client.delete(self.url(user.id))

        assert response.status_code == 401
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_delete_user_with_unauthorized_role(
        self, db: AsyncSession, async_client: AsyncClient, user_role: UserRole
    ):
        user = await UserFactory.create()
        user_with_unauthorized_role = await UserFactory.create(role=user_role)

        response = await async_client.delete(
            self.url(user.id),
            headers={API_KEY_HEADER_NAME: user_with_unauthorized_role.api_key},
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(User.id)))).scalar() == 2

    async def test_delete_user_with_nonexistent_user_id(self, async_client: AsyncClient, owner_auth_header: dict):
        user_id = uuid4()

        response = await async_client.delete(self.url(user_id), headers=owner_auth_header)

        assert response.status_code == 404
        assert response.json() == {"detail": f"User with id `{user_id}` not found"}
