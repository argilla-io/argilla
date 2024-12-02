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

        user_password_hash = user.password_hash

        response = await async_client.patch(
            self.url(user.id),
            headers=owner_auth_header,
            json={
                "first_name": "Updated First Name",
                "last_name": "Updated Last Name",
                "username": "updated_username",
                "role": UserRole.admin,
                "password": "new_password",
            },
        )

        assert response.status_code == 200

        updated_user = (await db.execute(select(User).filter_by(id=user.id))).scalar_one()
        assert updated_user.first_name == "Updated First Name"
        assert updated_user.last_name == "Updated Last Name"
        assert updated_user.username == "updated_username"
        assert updated_user.role == UserRole.admin
        assert updated_user.password_hash != user_password_hash

    async def test_update_user_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        user = await UserFactory.create()

        response = await async_client.patch(
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

        response = await async_client.patch(
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

        response = await async_client.patch(
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

    async def test_update_user_with_invalid_data(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        user = await UserFactory.create()

        response = await async_client.patch(
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

    async def test_update_user_with_duplicate_username(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        user1 = await UserFactory.create(username="user1")
        user2 = await UserFactory.create(username="user2")

        response = await async_client.patch(
            self.url(user2.id),
            headers=owner_auth_header,
            json={
                "username": user1.username,
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {"detail": "Username 'user1' already exists"}

    async def test_update_user_with_none_first_name(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        user = await UserFactory.create()

        response = await async_client.patch(
            self.url(user.id),
            headers=owner_auth_header,
            json={
                "first_name": None,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body"],
                            "msg": "Value error, The following keys must have non-null values: first_name",
                            "type": "value_error",
                        }
                    ]
                },
            }
        }

    async def test_update_user_with_none_last_name(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        user = await UserFactory.create()

        response = await async_client.patch(
            self.url(user.id),
            headers=owner_auth_header,
            json={
                "last_name": None,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(user.id),
            "api_key": user.api_key,
            "first_name": user.first_name,
            "last_name": None,
            "username": user.username,
            "role": user.role,
            "inserted_at": user.inserted_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

    async def test_update_user_with_none_username(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        user = await UserFactory.create()

        response = await async_client.patch(
            self.url(user.id),
            headers=owner_auth_header,
            json={
                "username": None,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body"],
                            "msg": "Value error, The following keys must have non-null values: username",
                            "type": "value_error",
                        }
                    ]
                },
            }
        }

    async def test_update_user_with_none_password(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        user = await UserFactory.create()

        response = await async_client.patch(
            self.url(user.id),
            headers=owner_auth_header,
            json={
                "password": None,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body"],
                            "msg": "Value error, The following keys must have non-null values: password",
                            "type": "value_error",
                        }
                    ]
                },
            }
        }
