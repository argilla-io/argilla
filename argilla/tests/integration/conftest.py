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


@pytest.fixture(scope="session")
def client() -> rg.Argilla:
    client = rg.Argilla()
    yield client


@pytest.fixture(autouse=True)
def cleanup(client: rg.Argilla):
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
