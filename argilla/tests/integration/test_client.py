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

from argilla import Argilla, Dataset, TextField, TextQuestion, Settings, User, Workspace
from argilla._exceptions import ArgillaError


@pytest.fixture
def dataset(client: Argilla) -> Dataset:
    return Dataset(
        name=f"test_dataset{uuid.uuid4()}",
        settings=Settings(fields=[TextField(name="text")], questions=[TextQuestion(name="question")]),
        client=client,
    ).create()


@pytest.fixture
def user(client: Argilla) -> User:
    user = User(username="test_user", password="test password").create()
    user.password = None  # to align with GET user result

    return user


@pytest.fixture
def workspace(client: Argilla) -> Workspace:
    return Workspace(name=f"test_workspace{uuid.uuid4()}").create()


# TODO: We can move this test suite to tests/unit once we have a mock client implementation
class TestClient:
    def test_get_resources(self, client: Argilla, workspace: Workspace, user: User, dataset: Dataset):
        assert client.workspaces(name=workspace.name) == workspace
        assert client.workspaces(id=workspace.id) == workspace
        assert client.workspaces(id=str(workspace.id)) == workspace
        assert client.workspaces(id=str(workspace.id), name="skip this name") == workspace

        assert client.users(username=user.username) == user
        assert client.users(id=user.id) == user
        assert client.users(id=str(user.id)) == user
        assert client.users(id=str(user.id), username="skip this username") == user

        assert client.datasets(name=dataset.name) == dataset
        assert client.datasets(id=dataset.id) == dataset
        assert client.datasets(id=str(dataset.id)) == dataset
        assert client.datasets(id=str(dataset.id), name="skip this name") == dataset

    def test_get_resources_warnings(self, client: Argilla):
        with pytest.warns(UserWarning, match="Workspace with id"):
            assert client.workspaces(id=uuid.uuid4()) is None

        with pytest.warns(UserWarning, match="User with id"):
            assert client.users(id=uuid.uuid4()) is None

        with pytest.warns(UserWarning, match="Dataset with id"):
            assert client.datasets(id=uuid.uuid4()) is None

        with pytest.warns(UserWarning, match="Workspace with name"):
            assert client.workspaces(name="missing") is None

        with pytest.warns(UserWarning, match="User with username"):
            assert client.users(username="missing") is None

        with pytest.warns(UserWarning, match="Dataset with name"):
            assert client.datasets(name="missing") is None

    def test_get_resource_with_missing_args(self, client: Argilla):
        with pytest.raises(ArgillaError):
            client.workspaces()

        with pytest.raises(ArgillaError):
            client.datasets()

        with pytest.raises(ArgillaError):
            client.users()

    def test_init_with_missing_api_url(self):
        with pytest.raises(ArgillaError):
            Argilla(api_url=None)

        with pytest.raises(ArgillaError):
            Argilla(api_url="")

    def test_init_with_missing_api_key(self):
        with pytest.raises(ArgillaError):
            Argilla(api_key=None)

        with pytest.raises(ArgillaError):
            Argilla(api_key="")
