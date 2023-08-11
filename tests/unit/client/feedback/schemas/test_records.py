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

from typing import Any, Dict, List, Optional, Union

import pytest
from argilla.client.feedback.schemas.records import (
    FeedbackRecord,
    RankingValueSchema,
    ResponseSchema,
    SuggestionSchema,
    ValueSchema,
)
from pydantic import ValidationError


@pytest.mark.parametrize(
    "schema_kwargs",
    [
        {
            "fields": {"text": "This is the first record", "label": "positive"},
            "metadata": {"first": True, "nested": {"more": "stuff"}},
            "responses": [
                {
                    "values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}},
                    "status": "submitted",
                }
            ],
            "suggestions": [
                {
                    "question_name": "question-1",
                    "type": "model",
                    "score": 0.9,
                    "value": "This is the first suggestion",
                    "agent": "agent-1",
                }
            ],
            "external_id": "entry-1",
        },
        {
            "fields": {"text": "This is the first record", "label": "positive"},
        },
        {
            "fields": {"text": "This is the first record", "label": "positive"},
            "metadata": {"first": True, "nested": {"more": "stuff"}},
        },
        {
            "fields": {"text": "This is the first record", "label": "positive"},
            "responses": [
                {
                    "values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}},
                    "status": "submitted",
                }
            ],
        },
        {
            "fields": {"text": "This is the first record", "label": "positive"},
            "suggestions": [
                {
                    "question_name": "question-1",
                    "type": "model",
                    "score": 0.9,
                    "value": "This is the first suggestion",
                    "agent": "agent-1",
                }
            ],
        },
    ],
)
def test_feedback_record(schema_kwargs: Dict[str, Any]) -> None:
    assert FeedbackRecord(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, suggestions, expected_warning, warning_match",
    [
        (
            {
                "fields": {"text": "This is the first record", "label": "positive"},
            },
            {
                "question_name": "question-1",
                "type": "model",
                "score": 0.9,
                "value": "This is the first suggestion",
                "agent": "agent-1",
            },
            None,
            None,
        ),
        (
            {
                "fields": {"text": "This is the first record", "label": "positive"},
                "suggestions": [{"question_name": "question-1", "value": "This is the first suggestion"}],
            },
            {
                "question_name": "question-1",
                "type": "model",
                "score": 0.9,
                "value": "This is the second suggestion",
                "agent": "agent-2",
            },
            UserWarning,
            "A suggestion for question `question-1` has already been provided",
        ),
    ],
)
def test_feedback_record_set_suggestions(
    schema_kwargs: Dict[str, Any],
    suggestions: Union[SuggestionSchema, List[SuggestionSchema], Dict[str, Any], List[Dict[str, Any]]],
    expected_warning: Optional[Warning],
    warning_match: Optional[str],
) -> None:
    record = FeedbackRecord(**schema_kwargs)
    with pytest.warns(expected_warning, match=warning_match):
        record.set_suggestions(suggestions)


@pytest.mark.parametrize(
    "schema_kwargs",
    [
        {"value": 1},
        {"value": "This is a value"},
        {"value": ["This is a value"]},
        {"value": [{"rank": 1, "value": "This is a value"}]},
    ],
)
def test_value_schema(schema_kwargs: Dict[str, Any]) -> None:
    assert ValueSchema(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs",
    [
        {"value": "question-1", "rank": 1},
    ],
)
def test_ranking_value_schema(schema_kwargs: Dict[str, Any]) -> None:
    assert RankingValueSchema(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, expected_exception, expected_exception_message",
    [
        (
            {"value": 1, "rank": 1},
            ValidationError,
            "str type expected",
        ),
        (
            {"value": "question-1", "rank": "string"},
            ValidationError,
            "value is not a valid integer",
        ),
        (
            {"value": "question-1", "rank": 0},
            ValidationError,
            "ensure this value is greater than or equal to 1",
        ),
    ],
)
def test_ranking_value_schema_errors(
    schema_kwargs: Dict[str, Any], expected_exception: Exception, expected_exception_message: str
) -> None:
    with pytest.raises(expected_exception, match=expected_exception_message):
        RankingValueSchema(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs",
    [
        {"user_id": "00000000-0000-0000-0000-000000000000", "values": {"question-1": {"value": 1}}},
        {"user_id": "00000000-0000-0000-0000-000000000000", "values": {"question-1": {"value": "This is a value"}}},
        {"user_id": "00000000-0000-0000-0000-000000000000", "values": {"question-1": {"value": ["This is a value"]}}},
        {
            "user_id": "00000000-0000-0000-0000-000000000000",
            "values": {"question-1": {"value": [{"rank": 1, "value": "This is a value"}]}},
        },
        {"values": {"question-1": {"value": 1}}},
        {"values": {"question-1": {"value": "This is a value"}}, "status": "submitted"},
        {"values": {"question-1": {"value": ["This is a value"]}}, "status": "discarded"},
    ],
)
def test_response_schema(schema_kwargs: Dict[str, Any]) -> None:
    assert ResponseSchema(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs",
    [
        {"question_name": "question-1", "value": 1},
        {"question_name": "question-1", "value": "This is a value"},
        {"question_name": "question-1", "value": ["This is a value"]},
        {"question_name": "question-1", "value": [{"rank": 1, "value": "This is a value"}]},
        {
            "question_name": "question-1",
            "value": [{"rank": 1, "value": "This is a value"}, {"rank": 2, "value": "This is a value"}],
            "score": 0.9,
            "type": "model",
            "agent": "agent-1",
        },
    ],
)
def test_suggestion_schema(schema_kwargs: Dict[str, Any]) -> None:
    assert SuggestionSchema(**schema_kwargs)
