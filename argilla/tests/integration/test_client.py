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
from argilla._exceptions import ArgillaAPIError, ArgillaError


class TestClient:
    def test_get_dataset_by_id(self, client: Argilla):
        dataset = Dataset(
            name=f"test_dataset{uuid.uuid4()}",
            settings=Settings(fields=[TextField(name="text")], questions=[TextQuestion(name="question")]),
        ).create()

        assert client.datasets(id=dataset.id) == dataset
        assert client.datasets(id=str(dataset.id)) == dataset
        assert client.datasets(id=str(dataset.id), name="skip this name") == dataset

        assert client.datasets(id=uuid.uuid4()) is None

    def test_get_user_by_id(self, client: Argilla):
        user = User(username="test_user", password="test password").create()
        user = client.users(username=user.username)

        assert client.users(id=user.id) == user
        assert client.users(id=str(user.id)) == user
        assert client.users(id=str(user.id), username="skip this username") == user
        assert client.users(id=uuid.uuid4()) is None

    def test_get_workspace_by_id(self, client: Argilla):
        workspace = Workspace(name=f"test_workspace{uuid.uuid4()}").create()

        assert client.workspaces(id=workspace.id) == workspace
        assert client.workspaces(id=str(workspace.id)) == workspace
        assert client.workspaces(id=str(workspace.id), name="skip this name") == workspace
        assert client.workspaces(id=uuid.uuid4()) is None

    def test_get_resource_with_missing_args(self, client: Argilla):
        with pytest.raises(ArgillaError):
            client.workspaces()

        with pytest.raises(ArgillaError):
            client.datasets()

        with pytest.raises(ArgillaError):
            client.users()
