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
import uuid

import pytest

from argilla import User, Argilla, Workspace
from argilla._exceptions import UnprocessableEntityError, ConflictError


class TestManageUsers:
    def test_create_user(self, client: Argilla):
        user = User(username=f"test_user_{uuid.uuid4()}", password="test_password")
        client.users.add(user)
        assert user.id is not None
        assert client.users(username=user.username).id == user.id

    def test_create_user_without_password(self, client: Argilla):
        user = User(username=f"test_user_{uuid.uuid4()}")
        with pytest.raises(expected_exception=UnprocessableEntityError):
            client.users.add(user)

    def test_delete_user(self, client: Argilla):
        user = User(username=f"test_delete_user_{uuid.uuid4()}", password="test_password")
        client.users.add(user)
        user.delete()
        assert not client.api.users.exist(user.id)

    def test_add_user_to_workspace(self, client: Argilla, workspace: Workspace):
        user = User(username=f"test_user_{uuid.uuid4()}", password="test_password")
        client.users.add(user)

        user = client.users(username=user.username)
        assert user.password is None

        user.add_to_workspace(workspace)
        assert user in workspace.users

    def test_update_user(self, client: Argilla):
        user = User(username=f"test_update_user_{uuid.uuid4()}", password="test_password")
        client.users.add(user)

        updated_username = f"updated_user_{uuid.uuid4()}"
        user.username = updated_username
        user.first_name = "Updated First Name"
        user.last_name = "Updated Last Name"
        user.role = "admin"
        user.update()

        updated_user = client.users(id=user.id)
        assert updated_user.username == updated_username
        assert updated_user.first_name == "Updated First Name"
        assert updated_user.last_name == "Updated Last Name"
        assert updated_user.role == "admin"

    def test_update_user_role(self, client: Argilla):
        user = User(username=f"test_update_user_{uuid.uuid4()}", password="test_password")
        client.users.add(user)

        user = client.users(username=user.username)

        user.role = "admin"
        user.update()

        updated_user = client.users(id=user.id)
        assert updated_user.role == "admin"

    def test_update_user_with_duplicate_username(self, client: Argilla):
        user1 = User(username=f"test_user1_{uuid.uuid4()}", password="test_password")
        user2 = User(username=f"test_user2_{uuid.uuid4()}", password="test_password")
        client.users.add(user1)
        client.users.add(user2)

        user2.username = user1.username
        with pytest.raises(expected_exception=UnprocessableEntityError):
            user2.update()
