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
import os
import random
import uuid
from string import ascii_lowercase
from tempfile import TemporaryDirectory

import pytest

import argilla as rg


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


def test_export_dataset_to_disk(dataset: rg.Dataset):
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
        output_dir = dataset.to_disk(path=temp_dir)

        records_path = os.path.join(output_dir, "records.json")
        assert os.path.exists(records_path)
        with open(records_path, "r") as f:
            exported_records = json.load(f)

        settings_path = os.path.join(output_dir, "settings.json")
        assert os.path.exists(settings_path)
        with open(settings_path, "r") as f:
            exported_settings = json.load(f)

        dataset_path = os.path.join(output_dir, "dataset.json")
        assert os.path.exists(dataset_path)
        with open(dataset_path, "r") as f:
            exported_dataset = json.load(f)

    assert len(exported_records) == len(mock_data)
    assert exported_records[0]["fields"]["text"] == "Hello World, how are you?"
    assert exported_records[0]["suggestions"]["label"]["value"] == "positive"

    assert exported_settings["fields"][0]["name"] == "text"
    assert exported_settings["questions"][0]["name"] == "label"

    assert exported_dataset["name"] == dataset.name


def test_import_dataset_from_disk(dataset: rg.Dataset, client):
    mock_data = [
        {
            "text": "1: Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "2: Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "3: Hello World, how are you?",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]
    dataset.records.log(records=mock_data)

    with TemporaryDirectory() as temp_dir:
        output_dir = dataset.to_disk(path=temp_dir)
        new_dataset = rg.Dataset.from_disk(output_dir, client=client)

    for i, record in enumerate(new_dataset.records(with_suggestions=True)):
        assert record.fields["text"] == mock_data[i]["text"]
        assert record.suggestions.label.value == mock_data[i]["label"]

    assert new_dataset.settings.fields[0].name == "text"
    assert new_dataset.settings.questions[0].name == "label"
