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

import datetime
from uuid import uuid4

from datasets import Sequence, Value

import argilla as rg
from argilla.records._io import HFDatasetsIO


class TestHFDatasetsIO:
    def test_to_datasets_with_partial_values_in_records(self):
        mock_dataset = rg.Dataset(
            name="test",
            settings=rg.Settings(
                fields=[
                    rg.TextField(name="field"),
                ],
                questions=[
                    rg.TextQuestion(name="question"),
                ],
            ),
        )
        records = [
            rg.Record(fields={"field": "The field"}, metadata={"a": "a"}, inserted_at=datetime.datetime.now()),
            rg.Record(fields={"field": "Other field", "other": "Field"}, metadata={"b": "b"}),
            rg.Record(fields={"field": "Again"}, suggestions=[rg.Suggestion("question", value="value")]),
            rg.Record(
                fields={"field": "Field"}, responses=[rg.Response("other_question", value="value", user_id=uuid4())]
            ),
            rg.Record(
                fields={"field": "The record field including more type of responses"},
                suggestions=[
                    rg.Suggestion("rating", value=1),
                    rg.Suggestion("ranking", value=["value1", "value2"]),
                    rg.Suggestion("spans", value=[{"start": 0, "end": 10, "label": "test"}]),
                ],
                responses=[
                    rg.Response("rating", value=1, user_id=uuid4()),
                    rg.Response("ranking", value=["value1", "value2"], user_id=uuid4()),
                    rg.Response("spans", value=[{"start": 0, "end": 10, "label": "test"}], user_id=uuid4()),
                ],
            ),
        ]

        ds = HFDatasetsIO.to_datasets(records, dataset=mock_dataset)
        assert ds.features == {
            "status": Value(dtype="string", id=None),
            "_server_id": Value(dtype="null", id=None),
            "a": Value(dtype="string", id=None),
            "b": Value(dtype="string", id=None),
            "field": Value(dtype="string", id=None),
            "id": Value(dtype="string", id=None),
            "inserted_at": Value(dtype="timestamp[ns, tz=UTC]", id=None),
            "updated_at": Value(dtype="timestamp[ns, tz=UTC]", id=None),
            "other": Value(dtype="string", id=None),
            "other_question.responses": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "other_question.responses.status": Sequence(feature=Value(dtype="null", id=None), length=-1, id=None),
            "other_question.responses.users": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "question.suggestion": Value(dtype="string", id=None),
            "question.suggestion.agent": Value(dtype="null", id=None),
            "question.suggestion.score": Value(dtype="null", id=None),
            "ranking.responses": Sequence(
                feature=Sequence(feature=Value(dtype="string", id=None), length=-1, id=None), length=-1, id=None
            ),
            "ranking.responses.status": Sequence(feature=Value(dtype="null", id=None), length=-1, id=None),
            "ranking.responses.users": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "ranking.suggestion": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "ranking.suggestion.agent": Value(dtype="null", id=None),
            "ranking.suggestion.score": Value(dtype="null", id=None),
            "rating.responses": Sequence(feature=Value(dtype="int64", id=None), length=-1, id=None),
            "rating.responses.status": Sequence(feature=Value(dtype="null", id=None), length=-1, id=None),
            "rating.responses.users": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "rating.suggestion": Value(dtype="int64", id=None),
            "rating.suggestion.agent": Value(dtype="null", id=None),
            "rating.suggestion.score": Value(dtype="null", id=None),
            "spans.responses": [
                [
                    {
                        "end": Value(dtype="int64", id=None),
                        "label": Value(dtype="string", id=None),
                        "start": Value(dtype="int64", id=None),
                    }
                ]
            ],
            "spans.responses.status": Sequence(feature=Value(dtype="null", id=None), length=-1, id=None),
            "spans.responses.users": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "spans.suggestion": [
                {
                    "end": Value(dtype="int64", id=None),
                    "label": Value(dtype="string", id=None),
                    "start": Value(dtype="int64", id=None),
                }
            ],
            "spans.suggestion.agent": Value(dtype="null", id=None),
            "spans.suggestion.score": Value(dtype="null", id=None),
        }
