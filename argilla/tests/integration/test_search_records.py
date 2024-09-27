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

from dataclasses import fields
from datetime import datetime

import pytest

from argilla import (
    Argilla,
    Workspace,
    Dataset,
    Settings,
    TextField,
    TextQuestion,
    LabelQuestion,
    Query,
    Record,
    Suggestion,
)


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


class TestSearchRecords:
    def test_search_records_by_id(self, client: Argilla, dataset: Dataset):
        dataset.records.log(
            [
                {"text": "The record text field", "id": 1},
                {"text": "The record text field", "id": 2},
            ]
        )

        records = list(dataset.records(query=Query(filter=("id", "==", 1))))
        assert len(records) == 1
        assert records[0].id == "1"

    def test_search_records_by_server_id(self, client: Argilla, dataset: Dataset):
        dataset.records.log(
            [
                {"text": "The record text field", "id": 1},
                {"text": "The record text field", "id": 2},
            ]
        )

        records = list(dataset.records)

        server_id = records[0]._server_id

        records = list(dataset.records(query=Query(filter=("_server_id", "==", server_id))))
        assert len(records) == 1
        assert records[0]._server_id == server_id

    def test_search_records_by_inserted_at(self, client: Argilla, dataset: Dataset):
        dataset.records.log(
            [
                {"text": "The record text field", "id": 1},
                {"text": "The record text field", "id": 2},
            ]
        )

        records = list(dataset.records(query=Query(filter=("inserted_at", "<=", datetime.utcnow()))))
        assert len(records) == 2
        assert records[0].id == "1"
        assert records[1].id == "2"

    def test_search_records_by_updated_at(self, client: Argilla, dataset: Dataset):
        dataset.records.log(
            [
                {"text": "The record text field", "id": 1},
                {"text": "The record text field", "id": 2},
            ]
        )

        records = list(dataset.records(query=Query(filter=("updated_at", "<=", datetime.utcnow()))))
        assert len(records) == 2
        assert records[0].id == "1"
        assert records[1].id == "2"

    def test_search_records_by_suggestion_agent(self, client: Argilla, dataset: Dataset):
        dataset.records.log(
            [
                Record(
                    id="1",
                    fields={"text": "The record text field"},
                    suggestions=[Suggestion(question_name="sentiment", agent="agent", value="positive")],
                ),
                Record(
                    id="2",
                    fields={"text": "The record text field"},
                    suggestions=[Suggestion(question_name="sentiment", agent="other-agent", value="positive")],
                ),
                {"text": "The record text field", "id": 3},
            ]
        )

        records = list(dataset.records(query=Query(filter=("sentiment.agent", "==", "agent"))))
        assert len(records) == 1
        assert records[0].id == "1"

    def test_search_records_by_suggestion_type(self, client: Argilla, dataset: Dataset):
        dataset.records.log(
            [
                Record(
                    id="1",
                    fields={"text": "The record text field"},
                    suggestions=[Suggestion(question_name="sentiment", type="human", value="positive")],
                ),
                Record(
                    id="2",
                    fields={"text": "The record text field"},
                    suggestions=[Suggestion(question_name="sentiment", type="model", value="positive")],
                ),
                {"text": "The record text field", "id": 3},
            ]
        )

        records = list(dataset.records(query=Query(filter=("sentiment.type", "==", "human"))))
        assert len(records) == 1
        assert records[0].id == "1"
