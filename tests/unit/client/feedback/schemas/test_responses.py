#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import pytest
from datetime import datetime
from uuid import uuid4

from argilla import ValueSchema
from argilla.client.sdk.users.models import UserModel, UserRole
from argilla.feedback import ResponseBuilder, ResponseSchema, ResponseStatus, SpanValueSchema, TextQuestion


def test_create_span_response_wrong_limits():
    with pytest.raises(ValueError, match="The end of the span must be greater than the start."):
        SpanValueSchema(start=10, end=8, label="test")


def test_create_response_from_builder():
    question = TextQuestion(name="text")
    user = UserModel(
        id=uuid4(),
        api_key="test",
        username="test",
        role=UserRole.annotator,
        first_name="test",
        last_name="test",
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    response = ResponseBuilder().status("draft").question_value(question, "Value for text").user(user).build()

    assert response.user_id == user.id
    assert response.status == ResponseStatus.draft
    assert question.name in response.values
    assert response.values[question.name].value == "Value for text"


def test_create_response_with_wrong_value():
    with pytest.raises(ValueError, match="Value 10 is not valid for question type text. Expected <class 'str'>."):
        ResponseBuilder().status("draft").question_value(TextQuestion(name="text"), 10).build()


def test_create_response_builder_from_response():
    response = ResponseSchema(
        user_id=uuid4(), status=ResponseStatus.draft, values={"text": ValueSchema(value="Value for text")}
    )

    builder = ResponseBuilder.from_response(response)

    new_response = builder.question_value(TextQuestion(name="other-text"), "Value for other text").build()

    assert new_response.user_id == response.user_id
    assert new_response.status == response.status
    assert "text" in new_response.values
    assert "other-text" in new_response.values
    assert new_response.values["text"].value == "Value for text"
    assert new_response.values["other-text"].value == "Value for other text"
