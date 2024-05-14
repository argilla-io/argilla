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

from tests.factories import UserFactory


@pytest.mark.asyncio
class TestsAuthentication:
    async def test_authenticate(self, async_client: AsyncClient):
        user = await UserFactory.create()

        response = await async_client.post(
            "/api/security/token",
            data={"username": user.username, "password": "1234"},
        )
        assert response.status_code == 200
        assert response.json()["access_token"]
        assert response.json()["token_type"] == "bearer"

    async def test_invalid_credentials(self, async_client: AsyncClient, owner: User):
        response = await async_client.post(
            "/api/security/token", data={"username": owner.username, "password": "invalid"}
        )
        assert response.status_code == 401
