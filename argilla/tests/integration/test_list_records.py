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
from string import ascii_lowercase

import pytest

from argilla import Argilla, Dataset, Settings, TextField, TextQuestion, Workspace, LabelQuestion


@pytest.fixture
def dataset(client: Argilla, workspace: Workspace, dataset_name: str) -> Dataset:
    settings = Settings(
        fields=[TextField(name="text")],
        questions=[
            TextQuestion(name="comment", use_markdown=False),
            LabelQuestion(name="sentiment", labels=["positive", "negative"], required=False),
        ],
    )
    dataset = Dataset(
        name=dataset_name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    dataset.create()
    yield dataset
    dataset.delete()


def test_list_records_with_start_offset(client: Argilla, dataset: Dataset):
    dataset.records.log(
        [
            {"text": "The record text field", "id": 1},
            {"text": "The record text field", "id": 2},
        ]
    )

    records = list(dataset.records(start_offset=1))
    assert len(records) == 1

    assert [record.to_dict() for record in records] == [
        {
            "_server_id": str(records[0]._server_id),
            "fields": {"text": "The record text field"},
            "id": "2",
            "status": "pending",
            "metadata": {},
            "responses": {},
            "suggestions": {},
            "vectors": {},
        }
    ]


def test_get_record_by_id(client: Argilla, dataset: Dataset):
    dataset.records.log(
        [
            {"text": "The record text field", "id": 1, "comment": "The comment", "sentiment": "positive"},
            {"text": "The record text field", "id": 2, "comment": "The comment", "sentiment": "negative"},
        ],
        mapping={
            "comment": "comment.response",
            "sentiment": "sentiment.response",
        },
    )

    record = list(dataset.records(with_responses=False))[0]
    assert not record.responses

    record.get()
    assert record.responses["comment"][0].value == "The comment"
    assert record.responses["sentiment"][0].value == "positive"


def test_list_records_with_responses(client: Argilla, dataset: Dataset):
    dataset.records.log(
        [
            {"text": "The record text field", "id": 1, "comment": "The comment", "sentiment": "positive"},
            {"text": "The record text field", "id": 2, "comment": "The comment", "sentiment": "negative"},
        ],
        mapping={
            "comment": "comment.response",
            "sentiment": "sentiment.response",
        },
    )

    records = list(dataset.records(with_responses=True))
    assert len(records) == 2

    assert records[0].responses["comment"][0].value == "The comment"
    assert records[0].responses["sentiment"][0].value == "positive"

    assert records[1].responses["comment"][0].value == "The comment"
    assert records[1].responses["sentiment"][0].value == "negative"


def test_list_records_with_updated_at_and_inserted_at(client: Argilla, dataset: Dataset):
    dataset.records.log(
        [
            {"text": "The record text field", "id": 1},
            {"text": "The record text field", "id": 2},
        ]
    )

    records = list(dataset.records(with_responses=True))
    assert len(records) == 2

    assert records[0].inserted_at
    assert records[0].updated_at

    assert records[1].inserted_at
    assert records[1].updated_at
