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

import pytest

from argilla import Response, User, Dataset, Settings, TextQuestion, TextField, Workspace
from argilla.records._resource import RecordResponses, Record


@pytest.fixture
def record():
    workspace = Workspace(name="workspace", id=uuid.uuid4())
    dataset = Dataset(
        workspace=workspace,
        settings=Settings(
            fields=[TextField(name="name")],
            allow_extra_metadata=True,
            questions=[
                TextQuestion(name="question_a"),
                TextQuestion(name="question_b"),
                TextQuestion(name="question_c"),
            ],
        ),
    )
    return Record(fields={"name": "John Doe"}, metadata={"age": 30}, _dataset=dataset)


class TestRecordResponses:
    def test_create_record_responses_for_single_user(self, record: Record):
        user = User(username="johndoe", id=uuid.uuid4())

        responses = [
            Response(question_name="question_a", value="answer_a", user_id=user.id),
            Response(question_name="question_b", value="answer_b", user_id=user.id),
            Response(question_name="question_c", value="answer_c", user_id=user.id),
        ]

        record_responses = RecordResponses(responses, record)

        assert record_responses["question_a"][0].value == "answer_a"
        assert record_responses["question_a"][0].user_id == user.id
        assert record_responses["question_b"][0].value == "answer_b"
        assert record_responses["question_b"][0].user_id == user.id
        assert record_responses["question_c"][0].value == "answer_c"
        assert record_responses["question_c"][0].user_id == user.id

    def test_create_record_responses_for_multiple_users(self, record: Record):
        user_a = User(username="johndoe", id=uuid.uuid4())
        user_b = User(username="janedoe", id=uuid.uuid4())

        responses = [
            Response(question_name="question_a", value="answer_a", user_id=user_a.id),
            Response(question_name="question_a", value="answer_a", user_id=user_b.id),
            Response(question_name="question_b", value="answer_b", user_id=user_a.id),
            Response(question_name="question_b", value="answer_b", user_id=user_b.id),
        ]

        record_responses = RecordResponses(responses, record)

        assert record_responses["question_a"][0].value == "answer_a"
        assert record_responses["question_a"][0].user_id == user_a.id
        assert record_responses["question_a"][1].value == "answer_a"
        assert record_responses["question_a"][1].user_id == user_b.id
        assert record_responses["question_b"][0].value == "answer_b"
        assert record_responses["question_b"][0].user_id == user_a.id

    def test_generate_responses_models_for_record_responses(self, record: Record):
        user = User(username="johndoe", id=uuid.uuid4())

        record_responses = RecordResponses(
            responses=[
                Response(question_name="question_a", value="answer_a", user_id=user.id),
                Response(question_name="question_b", value="answer_b", user_id=user.id),
            ],
            record=record,
        )

        models = record_responses.api_models()
        assert len(models) == 1
        assert models[0].model_dump() == {
            "user_id": str(user.id),
            "values": {
                "question_a": {"value": "answer_a"},
                "question_b": {"value": "answer_b"},
            },
            "status": "draft",
        }

    def test_generate_response_models_for_record_responses_with_multiple_users(self, record: Record):
        user_a = User(username="johndoe", id=uuid.uuid4())
        user_b = User(username="janedoe", id=uuid.uuid4())

        record_responses = RecordResponses(
            responses=[
                Response(question_name="question_a", value="answer_a", user_id=user_a.id),
                Response(question_name="question_a", value="answer_a", user_id=user_b.id),
                Response(question_name="question_b", value="answer_b", user_id=user_a.id),
                Response(question_name="question_b", value="answer_b", user_id=user_b.id),
            ],
            record=record,
        )

        models = record_responses.api_models()
        assert len(models) == 2
        assert models[0].model_dump() == {
            "user_id": str(user_a.id),
            "values": {
                "question_a": {"value": "answer_a"},
                "question_b": {"value": "answer_b"},
            },
            "status": "draft",
        }
        assert models[1].model_dump() == {
            "user_id": str(user_b.id),
            "values": {
                "question_a": {"value": "answer_a"},
                "question_b": {"value": "answer_b"},
            },
            "status": "draft",
        }
