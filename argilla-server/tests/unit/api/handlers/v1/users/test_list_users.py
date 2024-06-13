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
from argilla_server.models import User
from httpx import AsyncClient

from tests.factories import UserFactory


@pytest.mark.asyncio
class TestListUsers:
    def url(self) -> str:
        return "/api/v1/users"

    async def test_list_users(self, async_client: AsyncClient, owner: User, owner_auth_header: dict):
        user_a, user_b = await UserFactory.create_batch(2)

        response = await async_client.get(self.url(), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(owner.id),
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "username": owner.username,
                    "role": owner.role,
                    "api_key": owner.api_key,
                    "inserted_at": owner.inserted_at.isoformat(),
                    "updated_at": owner.updated_at.isoformat(),
                },
                {
                    "id": str(user_a.id),
                    "first_name": user_a.first_name,
                    "last_name": user_a.last_name,
                    "username": user_a.username,
                    "role": user_a.role,
                    "api_key": user_a.api_key,
                    "inserted_at": user_a.inserted_at.isoformat(),
                    "updated_at": user_a.updated_at.isoformat(),
                },
                {
                    "id": str(user_b.id),
                    "first_name": user_b.first_name,
                    "last_name": user_b.last_name,
                    "username": user_b.username,
                    "role": user_b.role,
                    "api_key": user_b.api_key,
                    "inserted_at": user_b.inserted_at.isoformat(),
                    "updated_at": user_b.updated_at.isoformat(),
                },
            ]
        }

    async def test_list_users_without_authentication(self, async_client: AsyncClient):
        response = await async_client.get(self.url())

        assert response.status_code == 401

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_list_users_with_unauthorized_role(self, async_client: AsyncClient, user_role: UserRole):
        user = await UserFactory.create(role=user_role)

        response = await async_client.get(self.url(), headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 403
