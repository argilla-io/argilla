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

import pytest

from argilla_sdk import User, Argilla


@pytest.fixture(scope="session", autouse=True)
def clean_environment(client: Argilla):
    for user in client.users:
        if user.username.startswith("test"):
            user.delete()
    yield
    for user in client.users:
        if user.username.startswith("test"):
            user.delete()


class TestManageUsers:
    def test_create_user(self, client: Argilla):
        user = User(username="test_user", password="test_password")
        client.users.add(user)
        assert user.id is not None
        assert client.users(username=user.username).id == user.id

    def test_delete_user(self, client: Argilla):
        user = User(username="test_delete_user", password="test_password")
        client.users.add(user)
        user.delete()
        assert not user.exists()
