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

from typing import Any, Dict, Type, Union

import pytest
from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    QuestionSchema,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from pydantic import ValidationError


def test_question_schema_name_validation_error() -> None:
    with pytest.raises(ValidationError, match=r"name\n  string does not match regex"):
        QuestionSchema(name="Completion-A")


@pytest.mark.parametrize(
    "schema_kwargs, expected_exception, expected_exception_message",
    [
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a"]},
            ValidationError,
            "ensure this value has at least 2 items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"], "visible_labels": 2},
            ValidationError,
            "ensure this value is greater than or equal to 3",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "a"]},
            ValidationError,
            "the list has duplicated items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": "a"},
            ValidationError,
            "(value is not a valid list)|(value is not a valid dict)",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": {"a": "a"}},
            ValidationError,
            "ensure this dict has at least 2 items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": {"a": "a", "b": "a"}},
            ValidationError,
            "ensure this dict has unique values",
        ),
    ],
)
def test_label_question_errors(
    schema_kwargs: Dict[str, Any], expected_exception: Exception, expected_exception_message: Union[str, None]
) -> None:
    with pytest.raises(expected_exception, match=expected_exception_message):
        LabelQuestion(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, expected_settings",
    [
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"]},
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": 20,
            },
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": {"a": "A", "b": "B"}},
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "A"}, {"value": "b", "text": "B"}],
                "visible_options": 20,
            },
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"], "visible_labels": 5},
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": 5,
            },
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"], "visible_labels": None},
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": None,
            },
        ),
    ],
)
def test_label_question(schema_kwargs: Dict[str, Any], expected_settings: Dict[str, Any]) -> None:
    assert LabelQuestion(**schema_kwargs).dict(include={"settings"})["settings"] == expected_settings


@pytest.mark.parametrize(
    "schema_kwargs, expected_exception, expected_exception_message",
    [
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a"]},
            ValidationError,
            "ensure this value has at least 2 items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"], "visible_labels": 2},
            ValidationError,
            "ensure this value is greater than or equal to 3",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "a"]},
            ValidationError,
            "the list has duplicated items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": "a"},
            ValidationError,
            "(value is not a valid list)|(value is not a valid dict)",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": {"a": "a"}},
            ValidationError,
            "ensure this dict has at least 2 items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": {"a": "a", "b": "a"}},
            ValidationError,
            "ensure this dict has unique values",
        ),
    ],
)
def test_multi_label_question_errors(
    schema_kwargs: Dict[str, Any], expected_exception: Exception, expected_exception_message: Union[str, None]
) -> None:
    with pytest.raises(expected_exception, match=expected_exception_message):
        MultiLabelQuestion(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, expected_settings",
    [
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"]},
            {
                "type": "multi_label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": 20,
            },
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": {"a": "A", "b": "B"}},
            {
                "type": "multi_label_selection",
                "options": [{"value": "a", "text": "A"}, {"value": "b", "text": "B"}],
                "visible_options": 20,
            },
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"], "visible_labels": 5},
            {
                "type": "multi_label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": 5,
            },
        ),
        (
            {"name": "a", "description": "a", "required": True, "labels": ["a", "b"], "visible_labels": None},
            {
                "type": "multi_label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": None,
            },
        ),
    ],
)
def test_multi_label_question(schema_kwargs: Dict[str, Any], expected_settings: Dict[str, Any]) -> None:
    assert MultiLabelQuestion(**schema_kwargs).dict(include={"settings"})["settings"] == expected_settings


@pytest.mark.parametrize(
    "schema_kwargs, expected_settings",
    [
        (
            {"name": "a", "description": "a", "required": True, "use_markdown": True},
            {"type": "text", "use_markdown": True},
        ),
        (
            {"name": "a", "description": "a", "required": True, "use_markdown": False},
            {"type": "text", "use_markdown": False},
        ),
    ],
)
def test_text_question(schema_kwargs: Dict[str, Any], expected_settings: Dict[str, Any]) -> None:
    assert TextQuestion(**schema_kwargs).dict(include={"settings"})["settings"] == expected_settings


@pytest.mark.parametrize(
    "schema_kwargs, expected_exception, expected_exception_message",
    [
        (
            {"name": "a", "description": "a", "required": True, "values": ["a", "b"]},
            ValidationError,
            "value is not a valid integer",
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": [1, 1, 1]},
            ValidationError,
            "the list has duplicated items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": [1]},
            ValidationError,
            "ensure this value has at least 2 items",
        ),
    ],
)
def test_rating_question_errors(
    schema_kwargs: Dict[str, Any], expected_exception: Type[Exception], expected_exception_message: Union[str, None]
) -> None:
    with pytest.raises(expected_exception, match=expected_exception_message):
        RatingQuestion(**schema_kwargs)


@pytest.mark.parametrize(
    ("schema_kwargs", "expected_warning_message"),
    [
        (
            {"name": "a", "description": "a", "required": True, "values": list(range(1, 12))},
            r"\`values\` list contains more than 10 elements, which is not supported from Argilla 1.14.0 onwards",
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": [0, 1, 2]},
            r"At least one \`value\` in \`values\` is out of range \[1, 10\], "
            r"which is not supported from Argilla 1.14.0 onwards",
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": [10, 11]},
            r"At least one \`value\` in \`values\` is out of range \[1, 10\], "
            r"which is not supported from Argilla 1.14.0 onwards",
        ),
    ],
)
def test_rating_question_warnings(schema_kwargs: Dict[str, Any], expected_warning_message: str) -> None:
    with pytest.warns(UserWarning, match=expected_warning_message):
        RatingQuestion(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, expected_settings",
    [
        (
            {"name": "a", "description": "a", "required": True, "values": [1, 2, 3]},
            {"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": 3}]},
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": [8, 9, 10]},
            {"type": "rating", "options": [{"value": 8}, {"value": 9}, {"value": 10}]},
        ),
    ],
)
def test_rating_question(schema_kwargs: Dict[str, Any], expected_settings: Dict[str, Any]) -> None:
    assert RatingQuestion(**schema_kwargs).dict(include={"settings"})["settings"] == expected_settings


@pytest.mark.parametrize(
    "schema_kwargs, expected_exception, expected_exception_message",
    [
        (
            {"name": "a", "description": "a", "required": True, "values": [1, 1]},
            ValidationError,
            "the list has duplicated items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": ["a"]},
            ValidationError,
            "ensure this value has at least 2 items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": {"a": "a"}},
            ValidationError,
            "ensure this dict has at least 2 items",
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": {1: "a", 2: "a"}},
            ValidationError,
            "ensure this dict has unique values",
        ),
    ],
)
def test_ranking_question_errors(
    schema_kwargs: Dict[str, Any], expected_exception: Exception, expected_exception_message: Union[str, None]
) -> None:
    with pytest.raises(expected_exception, match=expected_exception_message):
        RankingQuestion(**schema_kwargs)


@pytest.mark.parametrize(
    "schema_kwargs, expected_settings",
    [
        (
            {"name": "a", "description": "a", "required": True, "values": ["a", "b"]},
            {"type": "ranking", "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}]},
        ),
        (
            {"name": "a", "description": "a", "required": True, "values": {"a": "A", "b": "B"}},
            {"type": "ranking", "options": [{"value": "a", "text": "A"}, {"value": "b", "text": "B"}]},
        ),
    ],
)
def test_ranking_question(schema_kwargs: Dict[str, Any], expected_settings: Dict[str, Any]) -> None:
    assert RankingQuestion(**schema_kwargs).dict(include={"settings"})["settings"] == expected_settings
