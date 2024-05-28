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

from argilla_sdk import Record, Suggestion, Response
from argilla_sdk._models import MetadataModel


class TestRecords:
    def test_record_repr(self):
        record_id = uuid.uuid4()
        user_id = uuid.uuid4()
        record = Record(
            id=record_id,
            fields={"name": "John", "age": "30"},
            metadata={"key": "value"},
            suggestions=[Suggestion(question_name="question", value="answer")],
            responses=[Response(question_name="question", value="answer", user_id=user_id)],
        )
        assert (
            record.__repr__() == f"Record(id={record_id},"
            "fields={'name': 'John', 'age': '30'},"
            "metadata={'key': 'value'},"
            "suggestions={'question': {'value': 'answer', 'score': None, 'agent': None}},"
            f"responses={{'question': [{{'value': 'answer'}}]}})"
        )

    def test_update_record_metadata_by_key(self):
        record = Record(fields={"name": "John", "age": "30"}, metadata={"key": "value"})

        record.metadata["key"] = "new_value"
        record.metadata["new-key"] = "new_value"

        assert record.metadata == {"key": "new_value", "new-key": "new_value"}
        assert record.metadata.models == [
            MetadataModel(name="key", value="new_value"),
            MetadataModel(name="new-key", value="new_value"),
        ]

    def test_update_record_metadata_by_attribute(self):
        record = Record(fields={"name": "John", "age": "30"}, metadata={"key": "value"})

        record.metadata.key = "new_value"
        record.metadata.new_key = "new_value"

        assert record.metadata == {"key": "new_value", "new_key": "new_value"}
        assert record.metadata.models == [
            MetadataModel(name="key", value="new_value"),
            MetadataModel(name="new_key", value="new_value"),
        ]
