import pytest
from uuid import UUID, uuid4
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import UserRole
from argilla_server.models import User
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory

@pytest.mark.asyncio
class TestUpdateUser:
    def url(self, user_id: UUID) -> str:
        return f"/api/v1/users/{user_id}"

    async def test_update_user(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        user = await UserFactory.create()

        response = await async_client.put(
            self.url(user.id),
            headers=owner_auth_header,
            json={
                "first_name": "Updated First Name",
                "last_name": "Updated Last Name",
                "username": "updated_username",
                "role": UserRole.admin,
            },
        )

        assert response.status_code == 200

        updated_user = (await db.execute(select(User).filter_by(id=user.id))).scalar_one()
        assert updated_user.first_name == "Updated First Name"
        assert updated_user.last_name == "Updated Last Name"
        assert updated_user.username == "updated_username"
        assert updated_user.role == UserRole.admin

    async def test_update_user_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        user = await UserFactory.create()

        response = await async_client.put(
            self.url(user.id),
            json={
                "first_name": "Updated First Name",
                "last_name": "Updated Last Name",
                "username": "updated_username",
                "role": UserRole.admin,
            },
        )

        assert response.status_code == 401

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_update_user_with_unauthorized_role(
        self, db: AsyncSession, async_client: AsyncClient, user_role: UserRole
    ):
        user = await UserFactory.create()
        user_with_unauthorized_role = await UserFactory.create(role=user_role)

        response = await async_client.put(
            self.url(user.id),
            headers={API_KEY_HEADER_NAME: user_with_unauthorized_role.api_key},
            json={
                "first_name": "Updated First Name",
                "last_name": "Updated Last Name",
                "username": "updated_username",
                "role": UserRole.admin,
            },
        )

        assert response.status_code == 403

    async def test_update_user_with_nonexistent_user_id(self, async_client: AsyncClient, owner_auth_header: dict):
        user_id = uuid4()

        response = await async_client.put(
            self.url(user_id),
            headers=owner_auth_header,
            json={
                "first_name": "Updated First Name",
                "last_name": "Updated Last Name",
                "username": "updated_username",
                "role": UserRole.admin,
            },
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"User with id `{user_id}` not found"}

    async def test_update_user_with_invalid_data(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        user = await UserFactory.create()

        response = await async_client.put(
            self.url(user.id),
            headers=owner_auth_header,
            json={
                "first_name": "",
                "last_name": "Updated Last Name",
                "username": "updated_username",
                "role": "invalid_role",
            },
        )

        assert response.status_code == 422

    async def test_update_user_with_duplicate_username(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        user1 = await UserFactory.create(username="user1")
        user2 = await UserFactory.create(username="user2")

        response = await async_client.put(
            self.url(user2.id),
            headers=owner_auth_header,
            json={
                "username": "user1",
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Username `user1` already exists"}
