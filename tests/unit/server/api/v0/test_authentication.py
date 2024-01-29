import pytest
from httpx import AsyncClient

from argilla import User
from tests.factories import UserFactory


@pytest.mark.asyncio
class TestsAuthentication:
    async def authenticate(self, async_client: "AsyncClient"):
        user = await UserFactory.create()

        response = await async_client.post(
            "/api/security/token",
            data={"username": user.username, "password": "12345678"},
        )
        assert response.status_code == 200
        assert response.json()["access_token"]
        assert response.json()["token_type"] == "bearer"

    async def test_invalid_credentials(self, async_client: "AsyncClient", owner: User):
        response = await async_client.post(
            "/api/security/token", data={"username": owner.username, "password": "invalid"}
        )
        assert response.status_code == 401
