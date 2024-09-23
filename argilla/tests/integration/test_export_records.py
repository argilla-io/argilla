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
import random
import uuid
from pathlib import Path
from string import ascii_lowercase
from tempfile import TemporaryDirectory

import pytest
from PIL import Image
from datasets import Dataset as HFDataset

import argilla as rg
from argilla import Argilla


@pytest.fixture
def dataset(client) -> rg.Dataset:
    mock_dataset_name = "".join(random.choices(ascii_lowercase, k=16))
    settings = rg.Settings(
        fields=[
            rg.TextField(name="text"),
        ],
        questions=[
            rg.TextQuestion(name="label", use_markdown=False),
        ],
    )
    dataset = rg.Dataset(
        name=mock_dataset_name,
        settings=settings,
        client=client,
    )
    dataset.create()
    yield dataset
    dataset.delete()


def test_export_records_dict_flattened(client: Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)
    exported_records = dataset.records.to_dict(flatten=True)
    assert isinstance(exported_records, dict)
    assert isinstance(exported_records["id"], list)
    assert isinstance(exported_records["text"], list)
    assert isinstance(exported_records["label.suggestion"], list)
    assert exported_records["text"] == ["Hello World, how are you?"] * 3


def test_export_records_list_flattened(client: Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)
    exported_records = dataset.records.to_list(flatten=True)
    assert len(exported_records) == len(mock_data)
    assert isinstance(exported_records, list)
    assert isinstance(exported_records[0], dict)
    assert isinstance(exported_records[0]["id"], str)
    assert isinstance(exported_records[0]["text"], str)
    assert isinstance(exported_records[0]["label.suggestion"], str)
    assert exported_records[0]["text"] == "Hello World, how are you?"
    assert exported_records[0]["label.suggestion"] == "positive"
    assert exported_records[0]["label.suggestion.score"] is None


def test_export_record_list_with_filtered_records(client: Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)
    exported_records = dataset.records(query=rg.Query(query="hello")).to_list(flatten=True)
    assert len(exported_records) == len(mock_data)
    assert isinstance(exported_records, list)
    assert isinstance(exported_records[0], dict)
    assert isinstance(exported_records[0]["id"], str)
    assert isinstance(exported_records[0]["text"], str)
    assert isinstance(exported_records[0]["label.suggestion"], str)
    assert exported_records[0]["text"] == "Hello World, how are you?"
    assert exported_records[0]["label.suggestion"] == "positive"
    assert exported_records[0]["label.suggestion.score"] is None


def test_export_records_list_nested(client: Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)
    exported_records = dataset.records.to_list(flatten=False)
    assert len(exported_records) == len(mock_data)
    assert exported_records[0]["fields"]["text"] == "Hello World, how are you?"
    assert exported_records[0]["suggestions"]["label"]["value"] == "positive"
    assert exported_records[0]["suggestions"]["label"]["score"] is None


def test_export_records_dict_nested(client: Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]

    dataset.records.log(records=mock_data)
    exported_records = dataset.records.to_dict(flatten=False)
    assert isinstance(exported_records, dict)
    assert exported_records["fields"][0]["text"] == "Hello World, how are you?"
    assert exported_records["suggestions"][0]["label"]["value"] == "positive"


def test_export_records_dict_nested_orient_index(client: Argilla, dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)
    exported_records = dataset.records.to_dict(flatten=False, orient="index")
    assert isinstance(exported_records, dict)
    for mock_record, (id_, exported_record) in zip(mock_data, exported_records.items()):
        assert id_ == exported_record["id"]
        assert exported_record["fields"]["text"] == mock_record["text"]
        assert exported_record["suggestions"]["label"]["value"] == mock_record["label"]
        assert exported_record["id"] == str(mock_record["id"])


def test_export_records_to_json(dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)

    with TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "records.json"
        dataset.records.to_json(path=temp_file)
        with open(temp_file, "r") as f:
            exported_records = json.load(f)
    assert len(exported_records) == len(mock_data)
    assert exported_records[0]["fields"]["text"] == "Hello World, how are you?"
    assert exported_records[0]["suggestions"]["label"]["value"] == "positive"


def test_export_records_from_json(dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)

    with TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "records.json"
        dataset.records.to_json(path=temp_file)
        dataset.records.from_json(path=temp_file)

    for i, record in enumerate(dataset.records(with_suggestions=True)):
        assert record.fields["text"] == mock_data[i]["text"]
        assert record.suggestions["label"].value == mock_data[i]["label"]
        assert record.id == str(mock_data[i]["id"])


def test_export_records_to_hf_datasets(dataset: rg.Dataset):
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)
    hf_dataset = dataset.records.to_datasets()

    assert isinstance(hf_dataset, HFDataset)
    assert hf_dataset.num_rows == len(mock_data)
    assert "text" in hf_dataset.column_names
    assert "label.suggestion" in hf_dataset.column_names
    assert hf_dataset["text"][0] == "Hello World, how are you?"
    assert hf_dataset["id"][0] == str(mock_data[0]["id"])


def test_import_records_from_hf_dataset(dataset: rg.Dataset) -> None:
    mock_data = [
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": str(uuid.uuid4()),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": str(uuid.uuid4()),
        },
        {
            "text": "Hello World, how are you?",
            "label": "positive",
            "id": str(uuid.uuid4()),
        },
    ]
    mock_hf_dataset = HFDataset.from_list(mock_data)
    dataset.records.log(records=mock_hf_dataset)

    for i, record in enumerate(dataset.records(with_suggestions=True)):
        assert record.fields["text"] == mock_data[i]["text"]
        assert record.suggestions["label"].value == mock_data[i]["label"]
        assert record.id == str(mock_data[i]["id"])


def test_export_records_with_images_to_hf_datasets(client):
    mock_dataset_name = "".join(random.choices(ascii_lowercase, k=16))
    settings = rg.Settings(
        fields=[
            rg.ImageField(name="image"),
        ],
        questions=[
            rg.TextQuestion(name="label", use_markdown=False),
        ],
    )
    dataset = rg.Dataset(
        name=mock_dataset_name,
        settings=settings,
        client=client,
    )
    dataset.create()
    mock_data = [
        {
            "image": Image.new("RGB", (100, 100)),
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "image": Image.new("RGB", (100, 100)),
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "image": Image.new("RGB", (100, 100)),
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)
    hf_dataset = dataset.records.to_datasets()

    assert isinstance(hf_dataset, HFDataset)
    assert hf_dataset.num_rows == len(mock_data)
    assert "image" in hf_dataset.column_names
    assert "label.suggestion" in hf_dataset.column_names
    for i, image in enumerate(hf_dataset["image"]):
        assert isinstance(image, Image.Image)
