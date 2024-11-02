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

import argilla as rg
from argilla import ResponseStatus
from argilla.records._io import GenericIO


class TestGenericIO:
    def test_to_list_flatten(self):
        user_a, user_b, user_c = uuid4(), uuid4(), uuid4()

        record = rg.Record(
            fields={"field": "The field"},
            metadata={"key": "value"},
            responses=[
                rg.Response(question_name="q1", value="value", user_id=user_a, status=ResponseStatus.submitted),
                rg.Response(question_name="q2", value="value", user_id=user_a, status=ResponseStatus.submitted),
                rg.Response(question_name="q2", value="value", user_id=user_b, status=ResponseStatus.draft),
                rg.Response(question_name="q1", value="value", user_id=user_c),
            ],
            suggestions=[
                rg.Suggestion(question_name="q1", value="value", score=0.1, agent="test"),
                rg.Suggestion(question_name="q2", value="value", score=0.9),
            ],
        )

        records_list = GenericIO.to_list([record], flatten=True)
        assert records_list == [
            {
                "id": str(record.id),
                "status": "pending",
                "_server_id": None,
                "field": "The field",
                "key": "value",
                "q1.responses": ["value", "value"],
                "q1.responses.users": [str(user_a), str(user_c)],
                "q1.responses.status": ["submitted", None],
                "q2.responses": ["value", "value"],
                "q2.responses.users": [str(user_a), str(user_b)],
                "q2.responses.status": ["submitted", "draft"],
                "q1.suggestion": "value",
                "q1.suggestion.score": 0.1,
                "q1.suggestion.agent": "test",
                "q2.suggestion": "value",
                "q2.suggestion.score": 0.9,
                "q2.suggestion.agent": None,
            }
        ]
