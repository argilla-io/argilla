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

import pytest

from argilla_sdk import Record, Suggestion
from argilla_sdk.records._resource import RecordSuggestions


@pytest.fixture
def record():
    return Record(fields={"name": "John Doe"}, metadata={"age": 30})


class TestRecordSuggestions:
    def test_create_record_suggestions(self, record: Record):
        suggestions = RecordSuggestions(
            suggestions=[
                Suggestion("name", "John Doe", score=0.9),
                Suggestion("label", ["A", "B"], score=[0.8, 0.9]),
            ],
            record=record,
        )

        assert suggestions.record == record
        assert suggestions.name.value == "John Doe"
        assert suggestions.name.score == 0.9
        assert suggestions.label.value == ["A", "B"]
        assert suggestions.label.score == [0.8, 0.9]
