# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import uuid
from datetime import datetime

import httpx
import pytest
from pytest_httpx import HTTPXMock

import argilla as rg
from argilla._exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnprocessableEntityError,
)
from argilla._models import UserModel


class TestUserSerialization:
    def test_serialize(self):
        user = rg.User(
            id=uuid.uuid4(),
            username="test-user",
            first_name="Test",
            last_name="User",
        )

        assert user.serialize()["username"] == "test-user"
        assert user.serialize()["password"] is None

    def test_json_serialize(self):
        mock_uuid = uuid.uuid4()
        user = rg.User(
            id=mock_uuid,
            username="test-user",
            first_name="Test",
            last_name="User",
        )

        user_from_json = json.loads(user.serialize_json())
        assert user_from_json["username"] == "test-user"
        assert user_from_json["id"] == str(mock_uuid)

    def test_model_from_json(self):
        user_id = uuid.uuid4()
        user_json = {
            "id": user_id,
            "username": "test-user",
            "first_name": "Test",
            "last_name": "User",
            "role": "admin",
        }
        user = rg.User(**user_json)
        assert user.username == user_json["username"]
        assert str(user.id) == str(user_json["id"])


class TestUsers:
    @pytest.mark.parametrize(
        "status_code, expected_exception, expected_message",
        [
            (200, None, None),
            (400, BadRequestError, "BadRequestError"),
            (403, ForbiddenError, "ForbiddenError"),
            (404, NotFoundError, "NotFoundError"),
            (409, ConflictError, "ConflictError"),
            (422, UnprocessableEntityError, "UnprocessableEntityError"),
            (500, InternalServerError, "InternalServerError"),
        ],
    )
    def test_create_user(self, httpx_mock: HTTPXMock, status_code, expected_exception, expected_message):
        user_id = uuid.uuid4().hex
        mock_return_value = {
            "id": str(user_id),
            "username": "test-user",
            "password": "test-password",
            "first_name": "Test",
            "last_name": "User",
            "role": "admin",
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        api_url = "http://test_url"
        httpx_mock.add_response(
            json=mock_return_value, url=f"{api_url}/api/v1/users", method="POST", status_code=status_code
        )
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            user = rg.User(
                username="test-user",
                client=client,
            )
            if expected_exception:
                with pytest.raises(expected_exception, match=expected_message):
                    user.create()
            else:
                created_user = user.create()
                assert user.username == created_user.username
                assert user.id == created_user.id
                assert user.first_name == created_user.first_name
                assert user.last_name == created_user.last_name
                assert user.role == created_user.role
                assert user.inserted_at == created_user.inserted_at
                assert user.updated_at == created_user.updated_at

    @pytest.mark.parametrize(
        "status_code, expected_exception, expected_message",
        [
            (200, None, None),
            (400, BadRequestError, "BadRequestError"),
            (403, ForbiddenError, "ForbiddenError"),
            (404, NotFoundError, "NotFoundError"),
            (409, ConflictError, "ConflictError"),
            (422, UnprocessableEntityError, "UnprocessableEntityError"),
            (500, InternalServerError, "InternalServerError"),
        ],
    )
    def test_get_user(self, httpx_mock: HTTPXMock, status_code, expected_exception, expected_message):
        user_id = uuid.uuid4()
        mock_return_value = {
            "id": str(user_id),
            "username": "test-user",
            "password": "test-password",
            "first_name": "Test",
            "last_name": "User",
            "role": "admin",
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        api_url = "http://test_url"
        httpx_mock.add_response(
            json=mock_return_value, url=f"{api_url}/api/v1/users", method="POST", status_code=status_code
        )
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            user = rg.User(
                username="test-user",
                client=client,
            )
            if expected_exception:
                with pytest.raises(expected_exception, match=expected_message):
                    user.create()
            else:
                gotten_user = user.create()
                assert user.username == gotten_user.username
                assert user.id == gotten_user.id
                assert user.first_name == gotten_user.first_name
                assert user.last_name == gotten_user.last_name
                assert user.role == gotten_user.role
                assert user.inserted_at == gotten_user.inserted_at
                assert user.updated_at == gotten_user.updated_at

    def test_list_users(self, httpx_mock: HTTPXMock):
        mock_return_value = {
            "items": [
                {
                    "id": str(uuid.uuid4()),
                    "username": "test-user",
                    "first_name": "Test",
                    "last_name": "User",
                    "role": "admin",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "username": "another-test-user",
                    "first_name": "First",
                    "last_name": "Last",
                    "role": "annotator",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            ]
        }
        api_url = "http://test_url"
        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/users")
        with httpx.Client():
            client = rg.Argilla(api_url="http://test_url", api_key="admin.apikey")
            users = client.users
            assert len(users) == 2
            for i in range(len(users)):
                assert users[i].username == mock_return_value["items"][i]["username"]
                assert users[i].role == mock_return_value["items"][i]["role"]
                assert users[i].id == uuid.UUID(mock_return_value["items"][i]["id"])
                assert users[i].first_name == mock_return_value["items"][i]["first_name"]
                assert users[i].last_name == mock_return_value["items"][i]["last_name"]
                assert users[i].inserted_at == datetime.fromisoformat(mock_return_value["items"][i]["inserted_at"])
                assert users[i].updated_at == datetime.fromisoformat(mock_return_value["items"][i]["updated_at"])


class TestUsersAPI:
    def test_get_me(self, httpx_mock: HTTPXMock):
        mock_return_value = {
            "id": str(uuid.uuid4()),
            "username": "test-user",
            "first_name": "Test",
            "last_name": "User",
            "role": "admin",
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        api_url = "http://test_url"
        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/me")
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            user = client.api.users.get_me()
            assert user.username == mock_return_value["username"]
            assert user.id == uuid.UUID(mock_return_value["id"])
            assert user.role == mock_return_value["role"]
            assert user.first_name == mock_return_value["first_name"]
            assert user.last_name == mock_return_value["last_name"]
            assert user.inserted_at == datetime.fromisoformat(mock_return_value["inserted_at"])
            assert user.updated_at == datetime.fromisoformat(mock_return_value["updated_at"])

    def test_remove_user_from_workspace(self, httpx_mock: HTTPXMock):
        user_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        mock_return_value = {
            "id": str(user_id),
            "username": "test-user",
            "first_name": "Test",
            "last_name": "User",
            "role": "admin",
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        httpx_mock.add_response(
            url=f"http://test_url/api/v1/workspaces/{workspace_id}/users/{user_id}",
            method="DELETE",
            json=mock_return_value,
        )
        with httpx.Client():
            client = rg.Argilla(api_url="http://test_url", api_key="admin.apikey")
            client.api.users.delete_from_workspace(workspace_id, user_id)

    def test_delete_user(self, httpx_mock: HTTPXMock):
        user_id = uuid.uuid4()
        httpx_mock.add_response(url=f"http://test_url/api/v1/users/{user_id}", method="DELETE")
        with httpx.Client():
            client = rg.Argilla(api_url="http://test_url", api_key="admin.apikey")
            client.api.users.delete(user_id)

    def test_list_workspace_users(self, httpx_mock: HTTPXMock):
        workspace_id = uuid.uuid4()
        mock_return_value = {
            "items": [
                {
                    "id": str(uuid.uuid4()),
                    "username": "test-user",
                    "first_name": "Test",
                    "last_name": "User",
                    "role": "admin",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "username": "another-test-user",
                    "first_name": "Another",
                    "last_name": "User",
                    "role": "admin",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            ]
        }

        api_url = "http://test_url"
        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/workspaces/{workspace_id}/users")
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            users = client.api.users.list_by_workspace_id(workspace_id)
            assert len(users) == 2
            for i in range(len(users)):
                assert users[i].username == mock_return_value["items"][i]["username"]
                assert users[i].id == uuid.UUID(mock_return_value["items"][i]["id"])
                assert users[i].first_name == mock_return_value["items"][i]["first_name"]
                assert users[i].last_name == mock_return_value["items"][i]["last_name"]
                assert users[i].role == mock_return_value["items"][i]["role"]
                assert users[i].inserted_at == datetime.fromisoformat(mock_return_value["items"][i]["inserted_at"])
                assert users[i].updated_at == datetime.fromisoformat(mock_return_value["items"][i]["updated_at"])

    def test_create_user(self, httpx_mock: HTTPXMock):
        user_id = uuid.uuid4()
        mock_return_value = {
            "id": str(user_id),
            "username": "test-user",
            "first_name": "Test",
            "last_name": "User",
            "role": "admin",
            "password": "test-password",
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        api_url = "http://test_url"

        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/users", method="POST", status_code=200)
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            user_create = UserModel(username="test-user", password="test-password")
            user = client.api.users.create(user_create)
            assert user.id == user_id
            assert user.username == "test-user"
            assert user.password == "test-password"
