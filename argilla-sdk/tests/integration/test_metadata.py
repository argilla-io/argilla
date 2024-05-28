# Copyright 2024-present, Argilla, Inc.
# TODO: This license is not consistent with the license used in the project.
#       Delete the inconsistent license and above line and rerun pre-commit to insert a good license.
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
from string import ascii_lowercase

import argilla_sdk as rg
import pytest
from argilla_sdk import Argilla, Dataset, LabelQuestion, Settings, TextField, Workspace


@pytest.fixture
def workspace(client: Argilla) -> Workspace:
    workspace = client.workspaces("test-workspace")
    if not workspace.exists():
        workspace.create()
    yield workspace

    for dataset in workspace.list_datasets():
        client.api.datasets.delete(dataset.id)

    workspace.delete()


@pytest.fixture
def dataset_with_metadata(client: Argilla, workspace: Workspace) -> Dataset:
    name = "".join(random.choices(ascii_lowercase, k=16))
    settings = Settings(
        fields=[TextField(name="text")],
        questions=[LabelQuestion(name="label", labels=["positive", "negative"])],
        metadata=[
            rg.TermsMetadataProperty(name="category", options=["A", "B", "C"]),
        ],
    )
    dataset = Dataset(
        name=name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    dataset.create()
    dataset.get()
    return dataset


def test_create_dataset_with_metadata(client: Argilla, workspace: Workspace) -> Dataset:
    name = "".join(random.choices(ascii_lowercase, k=16))
    settings = Settings(
        fields=[TextField(name="text")],
        questions=[LabelQuestion(name="label", labels=["positive", "negative"])],
        metadata=[
            rg.TermsMetadataProperty(name="category", options=["A", "B", "C"]),
        ],
    )
    dataset = Dataset(
        name=name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    dataset.create()
    dataset.get()

    assert dataset.settings.metadata[0].name == "category"


@pytest.mark.parametrize(
    "min, max, type",
    [
        (0, 1, rg.FloatMetadataProperty),
        (None, None, rg.FloatMetadataProperty),
        (0, 1, rg.IntegerMetadataProperty),
        (None, None, rg.IntegerMetadataProperty),
    ],
)
def test_create_dataset_with_numerical_metadata(client: Argilla, workspace: Workspace, min, max, type) -> Dataset:
    name = "".join(random.choices(ascii_lowercase, k=16))
    settings = Settings(
        fields=[TextField(name="text")],
        questions=[LabelQuestion(name="label", labels=["positive", "negative"])],
        metadata=[
            type(name="price", min=min, max=max),
        ],
    )
    dataset = Dataset(
        name=name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    dataset.create()
    gotten_dataset = dataset.get()

    assert gotten_dataset.settings.metadata[0].name == "price"
    assert gotten_dataset.settings.metadata[0].min == min
    assert gotten_dataset.settings.metadata[0].max == max


def test_add_record_with_metadata(dataset_with_metadata: Dataset):
    records = [
        {"text": "text", "label": "positive", "category": "A"},
        {"text": "text", "label": "negative", "category": "B"},
    ]

    dataset_with_metadata.records.add(records)

    for idx, record in enumerate(dataset_with_metadata.records):
        assert record.metadata.category == records[idx]["category"]
        assert record.metadata["category"] == records[idx]["category"]
        assert len(record.metadata) == 1
        models = record.metadata.models
        assert models[0].value == records[idx]["category"]
        assert models[0].name == "category"


def test_add_record_with_mapped_metadata(dataset_with_metadata: Dataset):
    records = [
        {"text": "text", "label": "positive", "my_category": "A"},
        {"text": "text", "label": "negative", "my_category": "B"},
    ]

    dataset_with_metadata.records.add(records, mapping={"my_category": "category"})

    for idx, record in enumerate(dataset_with_metadata.records):
        assert record.metadata.category == records[idx]["my_category"]
        assert record.metadata["category"] == records[idx]["my_category"]
        assert len(record.metadata) == 1
        models = record.metadata.models
        assert models[0].value == records[idx]["my_category"]
        assert models[0].name == "category"
