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
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


@pytest.mark.asyncio
class TestCreateUser:
    def url(self) -> str:
        return "/api/v1/users"

    async def test_create_user(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(User.id)))).scalar() == 2
        user = (await db.execute(select(User).filter_by(username="username"))).scalar_one()

        response_json = response.json()
        assert response_json == {
            "id": str(user.id),
            "first_name": "First name",
            "last_name": "Last name",
            "username": "username",
            "role": UserRole.annotator,
            "api_key": user.api_key,
            "inserted_at": user.inserted_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

    async def test_create_user_with_first_name_including_leading_and_trailing_spaces(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "  First name  ",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(User.id)))).scalar() == 2
        user = (await db.execute(select(User).filter_by(username="username"))).scalar_one()

        assert response.json()["first_name"] == "First name"
        assert user.first_name == "First name"

    async def test_create_user_with_last_name_including_leading_and_trailing_spaces(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "  Last name  ",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(User.id)))).scalar() == 2
        user = (await db.execute(select(User).filter_by(username="username"))).scalar_one()

        assert response.json()["last_name"] == "Last name"
        assert user.last_name == "Last name"

    async def test_create_user_without_last_name(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(User.id)))).scalar() == 2
        user = (await db.execute(select(User).filter_by(username="username"))).scalar_one()

        assert response.json()["last_name"] == None
        assert user.last_name == None

    async def test_create_user_with_non_default_role(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
                "role": UserRole.owner,
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(User.id)))).scalar() == 2
        user = (await db.execute(select(User).filter_by(username="username"))).scalar_one()

        assert response.json()["role"] == UserRole.owner
        assert user.role == UserRole.owner

    async def test_create_user_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        response = await async_client.post(
            self.url(),
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 401
        assert (await db.execute(select(func.count(User.id)))).scalar() == 0

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_create_user_with_unauthorized_role(
        self, db: AsyncSession, async_client: AsyncClient, user_role: UserRole
    ):
        user = await UserFactory.create(role=user_role)

        response = await async_client.post(
            self.url(),
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    async def test_create_user_with_existent_username(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        await UserFactory.create(username="username")

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "User username `username` is not unique"}

        assert (await db.execute(select(func.count(User.id)))).scalar() == 2

    async def test_create_user_with_invalid_username(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "invalid username",
                "password": "12345678",
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    async def test_create_user_with_invalid_min_length_first_name(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    async def test_create_user_with_invalid_min_length_last_name(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "",
                "username": "username",
                "password": "12345678",
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    async def test_create_user_with_invalid_min_length_password(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "1234",
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    async def test_create_user_with_invalid_max_length_password(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "p" * 101,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1

    async def test_create_user_with_invalid_role(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "first_name": "First name",
                "last_name": "Last name",
                "username": "username",
                "password": "12345678",
                "role": "invalid role",
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(User.id)))).scalar() == 1
