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

from argilla import Record, Suggestion, Response
from argilla._models import MetadataModel


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
        assert record.metadata.api_models() == [
            MetadataModel(name="key", value="new_value"),
            MetadataModel(name="new-key", value="new_value"),
        ]

    def test_update_record_fields(self):
        record = Record(fields={"name": "John"})

        record.fields.update({"name": "Jane", "age": "30"})
        record.fields["new_field"] = "value"

        assert record.fields == {"name": "Jane", "age": "30", "new_field": "value"}

    def test_update_record_vectors(self):
        record = Record(fields={"name": "John"}, vectors={"vector": [1.0, 2.0, 3.0]})

        record.vectors["new-vector"] = [1.0, 2.0, 3.0]
        assert record.vectors == {"vector": [1.0, 2.0, 3.0], "new-vector": [1.0, 2.0, 3.0]}

