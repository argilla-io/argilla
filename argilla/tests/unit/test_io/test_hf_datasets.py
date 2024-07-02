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

from uuid import uuid4

from datasets import Value, Sequence

import argilla as rg
from argilla.records._io import HFDatasetsIO


class TestHFDatasetsIO:
    def test_to_datasets_with_partial_values_in_records(self):
        records = [
            rg.Record(fields={"field": "The field"}, metadata={"a": "a"}),
            rg.Record(fields={"field": "Other field", "other": "Field"}, metadata={"b": "b"}),
            rg.Record(fields={"field": "Again"}, suggestions=[rg.Suggestion("question", value="value")]),
            rg.Record(
                fields={"field": "Field"}, responses=[rg.Response("other_question", value="value", user_id=uuid4())]
            ),
        ]

        ds = HFDatasetsIO.to_datasets(records)
        assert ds.features == {
            "_server_id": Value(dtype="null", id=None),
            "id": Value(dtype="string", id=None),
            "field": Value(dtype="string", id=None),
            "other": Value(dtype="string", id=None),
            "a": Value(dtype="string", id=None),
            "b": Value(dtype="string", id=None),
            "question.suggestion": Value(dtype="string", id=None),
            "question.suggestion.agent": Value(dtype="null", id=None),
            "question.suggestion.score": Value(dtype="null", id=None),
            "other_question.responses": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "other_question.responses.users": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
        }
