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

import argilla as rg
from argilla import Argilla, Workspace


@pytest.fixture(scope="session")
def client() -> rg.Argilla:
    client = rg.Argilla()

    if len(list(client.workspaces)) == 0:
        client.workspaces.add(rg.Workspace(name=f"test_{uuid.uuid4()}"))

    yield client

    _cleanup(client)


def _cleanup(client: rg.Argilla):
    for workspace in client.workspaces:
        if workspace.name.startswith("test_"):
            for dataset in workspace.datasets:
                dataset.delete()
            workspace.delete()

    for user in client.users:
        if user.username.startswith("test_"):
            user.delete()


@pytest.fixture()
def dataset_name() -> str:
    """use this fixture to autogenerate a safe dataset name for tests"""
    return f"test_dataset_{uuid.uuid4()}"


@pytest.fixture()
def username() -> str:
    return f"test_username_{uuid.uuid4()}"


@pytest.fixture
def workspace(client: Argilla) -> Workspace:
    ws_name = f"test-{uuid.uuid4()}"

    workspace = client.workspaces(ws_name)
    if workspace is None:
        workspace = Workspace(name=ws_name).create()
    yield workspace

    for dataset in workspace.list_datasets():
        dataset.delete()

    workspace.delete()
