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


@pytest.fixture
def dataset(client: rg.Argilla) -> rg.Dataset:
    workspace = client.workspaces[0]
    mock_dataset_name = f"test_delete_records_{uuid.uuid1()}"
    settings = rg.Settings(
        allow_extra_metadata=True,
        fields=[
            rg.TextField(name="text"),
        ],
        questions=[
            rg.TextQuestion(name="label", use_markdown=False),
        ],
    )
    dataset = rg.Dataset(
        name=mock_dataset_name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    dataset.create()
    return dataset


def test_delete_records(client: rg.Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
    ]

    dataset.records.log(records=mock_data)
    records_to_delete = list(dataset.records)[:2]
    dataset.records.delete(records_to_delete)
    dataset_records = list(dataset.records)

    assert len(dataset_records) == 1
    assert dataset_records[0].id == str(mock_data[2]["id"])

    for record in dataset_records:
        assert record.id not in [record.id for record in records_to_delete]


def test_delete_single_record(client: rg.Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
    ]

    dataset.records.log(records=mock_data)
    records_to_delete = [list(dataset.records)[1]]
    dataset.records.delete(records_to_delete)
    dataset_records = list(dataset.records)

    assert len(dataset_records) == 2
    assert dataset_records[0].id == str(mock_data[0]["id"])
    assert dataset_records[1].id == str(mock_data[2]["id"])
    assert mock_data[1]["id"] not in [record.id for record in dataset_records]


def test_delete_records_with_batch_support(client: rg.Argilla, dataset: rg.Dataset):
    records = [rg.Record(id=uuid.uuid4(), fields={"text": f"Field for record {i}"}) for i in range(0, 1000)]

    dataset.records.log(records)
    all_records = list(dataset.records)
    dataset.records.delete(all_records)

    assert len(list(dataset.records)) == 0
