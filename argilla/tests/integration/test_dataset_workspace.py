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

import random
import uuid

import pytest

import argilla as rg
from argilla._exceptions import NotFoundError


@pytest.fixture
def dataset(client: rg.Argilla, dataset_name: str):
    ws = client.workspaces[0]
    dataset = rg.Dataset(
        name=dataset_name,
        settings=rg.Settings(
            fields=[
                rg.TextField(name="text"),
            ],
            questions=[
                rg.TextQuestion(name="response"),
            ],
        ),
        workspace=ws,
        client=client,
    )
    dataset.create()
    yield dataset
    dataset.delete()


def test_dataset_with_workspace(client: rg.Argilla, dataset_name: str):
    ws = client.workspaces[0]
    dataset = rg.Dataset(
        name=dataset_name,
        settings=rg.Settings(
            fields=[
                rg.TextField(name="text"),
            ],
            questions=[
                rg.TextQuestion(name="response"),
            ],
        ),
        workspace=ws,
        client=client,
    )
    dataset.create()
    assert isinstance(dataset, rg.Dataset)
    assert client.api.datasets.exists(dataset.id)
    assert dataset.workspace == ws


def test_dataset_with_workspace_name(client: rg.Argilla, dataset_name: str):
    ws = client.workspaces[0]
    dataset = rg.Dataset(
        name=dataset_name,
        settings=rg.Settings(
            fields=[
                rg.TextField(name="text"),
            ],
            questions=[
                rg.TextQuestion(name="response"),
            ],
        ),
        workspace=ws.name,
        client=client,
    )
    dataset.create()
    assert isinstance(dataset, rg.Dataset)
    assert dataset.id is not None
    assert client.api.datasets.exists(dataset.id)
    assert dataset.workspace == ws


def test_dataset_with_incorrect_workspace_name(client: rg.Argilla, dataset_name: str):
    with pytest.raises(expected_exception=NotFoundError):
        rg.Dataset(
            name=dataset_name,
            settings=rg.Settings(
                fields=[
                    rg.TextField(name="text"),
                ],
                questions=[
                    rg.TextQuestion(name="response"),
                ],
            ),
            workspace=f"non_existing_workspace",
            client=client,
        ).create()


def test_dataset_with_default_workspace(client: rg.Argilla, dataset_name: str):
    dataset = rg.Dataset(
        name=dataset_name,
        settings=rg.Settings(
            fields=[
                rg.TextField(name="text"),
            ],
            questions=[
                rg.TextQuestion(name="response"),
            ],
        ),
        client=client,
    )
    dataset.create()
    assert isinstance(dataset, rg.Dataset)
    assert client.api.datasets.exists(dataset.id)
    assert dataset.workspace == client.workspaces[0]


def test_retrieving_dataset(client: rg.Argilla, dataset: rg.Dataset):
    ws = client.workspaces[0]
    dataset = client.datasets(dataset.name, workspace=ws)
    assert isinstance(dataset, rg.Dataset)
    assert client.api.datasets.exists(dataset.id)


def test_retrieving_dataset_on_name(client: rg.Argilla, dataset: rg.Dataset):
    ws = client.workspaces[0]
    dataset = client.datasets(dataset.name, workspace=ws.name)
    assert isinstance(dataset, rg.Dataset)
    assert client.api.datasets.exists(dataset.id)


def test_retrieving_dataset_on_default(client: rg.Argilla, dataset: rg.Dataset):
    dataset = client.datasets(dataset.name)
    assert isinstance(dataset, rg.Dataset)
    assert client.api.datasets.exists(dataset.id)
