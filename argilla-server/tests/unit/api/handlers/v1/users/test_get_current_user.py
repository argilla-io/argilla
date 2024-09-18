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
from argilla_server.models import User
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGetCurrentUser:
    def url(self) -> str:
        return "/api/v1/me"

    async def test_get_current_user(self, async_client: AsyncClient, owner: User, owner_auth_header: dict):
        response = await async_client.get(self.url(), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(owner.id),
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "username": owner.username,
            "role": owner.role,
            "api_key": owner.api_key,
            "inserted_at": owner.inserted_at.isoformat(),
            "updated_at": owner.updated_at.isoformat(),
        }

    async def test_get_current_user_without_authentication(self, async_client: AsyncClient):
        response = await async_client.get(self.url())

        assert response.status_code == 401
