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
from uuid import uuid4

from argilla.feedback import (
    FeedbackDataset,
    ResponseSchema,
    ResponseStatus,
    SpanValueSchema,
    TextQuestion,
    ValueSchema,
)


def test_create_span_response_wrong_limits():
    with pytest.raises(ValueError, match="The end of the span must be greater than the start."):
        SpanValueSchema(start=10, end=8, label="test")


def test_create_response():
    question = TextQuestion(name="text")
    response = ResponseSchema(status="draft").with_question_value(question, "Value for text")

    assert response.status == ResponseStatus.draft
    assert question.name in response.values
    assert response.values[question.name].value == "Value for text"


def test_create_responses_with_multiple_questions():
    question1 = TextQuestion(name="text")
    question2 = TextQuestion(name="text2")
    response = (
        ResponseSchema(status="draft")
        .with_question_value(question1, "Value for text")
        .with_question_value(question2, "Value for text2")
    )

    assert response.status == ResponseStatus.draft
    assert question1.name in response.values
    assert response.values[question1.name].value == "Value for text"
    assert question2.name in response.values
    assert response.values[question2.name].value == "Value for text2"


def test_create_response_with_wrong_value():
    with pytest.raises(ValueError, match="Value 10 is not valid for question type text. Expected <class 'str'>."):
        ResponseSchema(status="draft").with_question_value(TextQuestion(name="text"), 10)
