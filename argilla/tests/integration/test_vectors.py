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
from datetime import datetime

import pytest

import argilla as rg


@pytest.fixture
def dataset(client: rg.Argilla, dataset_name: str) -> rg.Dataset:
    workspace = client.workspaces[0]
    settings = rg.Settings(
        fields=[rg.TextField(name="text")],
        questions=[rg.LabelQuestion(name="label", labels=["positive", "negative"])],
        vectors=[rg.VectorField(name="vector", dimensions=10)],
    )
    dataset = rg.Dataset(
        name=dataset_name,
        workspace=workspace,
        settings=settings,
        client=client,
    )
    dataset.create()
    yield dataset
    dataset.delete()


def test_vectors(client: rg.Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
    ]
    dataset.records.log(records=mock_data)

    dataset_records = list(dataset.records(with_responses=True, with_suggestions=True, with_vectors=["vector"]))
    assert dataset_records[0].id == str(mock_data[0]["id"])
    assert dataset_records[1].id == str(mock_data[1]["id"])
    assert dataset_records[2].id == str(mock_data[2]["id"])
    assert dataset_records[0].vectors["vector"] == mock_data[0]["vector"]
    assert dataset_records[1].vectors["vector"] == mock_data[1]["vector"]
    assert dataset_records[2].vectors["vector"] == mock_data[2]["vector"]


def test_vectors_return_with_bool(client: rg.Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
    ]
    dataset.records.log(records=mock_data)

    dataset_records = list(dataset.records(with_responses=True, with_suggestions=True, with_vectors=True))
    assert dataset_records[0].id == str(mock_data[0]["id"])
    assert dataset_records[1].id == str(mock_data[1]["id"])
    assert dataset_records[2].id == str(mock_data[2]["id"])
    assert dataset_records[0].vectors["vector"] == mock_data[0]["vector"]
    assert dataset_records[1].vectors["vector"] == mock_data[1]["vector"]
    assert dataset_records[2].vectors["vector"] == mock_data[2]["vector"]


def test_vectors_return_with_name(client: rg.Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
            "vector": [random.random() for _ in range(10)],
        },
    ]
    dataset.records.log(records=mock_data)

    dataset_records = list(dataset.records(with_responses=True, with_suggestions=True, with_vectors="vector"))
    assert dataset_records[0].id == str(mock_data[0]["id"])
    assert dataset_records[1].id == str(mock_data[1]["id"])
    assert dataset_records[2].id == str(mock_data[2]["id"])
    assert dataset_records[0].vectors["vector"] == mock_data[0]["vector"]
    assert dataset_records[1].vectors["vector"] == mock_data[1]["vector"]
    assert dataset_records[2].vectors["vector"] == mock_data[2]["vector"]
