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

from typing import Any, Dict, Union

import pytest
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
)
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    LabelQuestionUnification,
    MultiLabelQuestionStrategy,
    MultiLabelQuestionUnification,
    RatingQuestionStrategy,
    RatingQuestionUnification,
    UnificatiedValueSchema,
)
from pydantic import ValidationError


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
    "strategy, unified_response",
    [
        ("mean", [{"value": str(int(5 / 3)), "strategy": "mean"}]),
        ("majority", [{"value": "2", "strategy": "majority"}]),
        ("max", [{"value": "2", "strategy": "max"}]),
        ("min", [{"value": "1", "strategy": "min"}]),
    ],
)
def test_rating_question_strategy(strategy, unified_response):
    question_name = "rating"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": "1"}}},
            {"values": {question_name: {"value": "2"}}},
            {"values": {question_name: {"value": "2"}}},
        ],
    }
    record = FeedbackRecord(**records_payload)
    question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "values": ["1", "2"],
    }
    question = RatingQuestion(**question_payload)
    strategy = RatingQuestionStrategy(strategy)
    strategy.unify_responses([record], question)
    unified_response = [UnificatiedValueSchema(**resp) for resp in unified_response]
    assert record._unified_responses[question_name] == unified_response
    assert RatingQuestionUnification(question=question, strategy=strategy)


@pytest.mark.parametrize(
    "strategy, unified_response",
    [
        ("majority", [{"value": "2", "strategy": "majority"}]),
        (
            "disagreement",
            [
                {"value": "1", "strategy": "disagreement"},
                {"value": "2", "strategy": "disagreement"},
                {"value": "2", "strategy": "disagreement"},
            ],
        ),
    ],
)
def test_label_question_strategy(strategy, unified_response):
    question_name = "rating"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": "1"}}},
            {"values": {question_name: {"value": "2"}}},
            {"values": {question_name: {"value": "2"}}},
        ],
    }
    record = FeedbackRecord(**records_payload)
    question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "labels": ["1", "2"],
    }
    question = LabelQuestion(**question_payload)
    strategy = LabelQuestionStrategy(strategy)
    strategy.unify_responses([record], question)
    unified_response = [UnificatiedValueSchema(**resp) for resp in unified_response]
    assert record._unified_responses[question_name] == unified_response
    assert LabelQuestionUnification(question=question, strategy=strategy)


@pytest.mark.parametrize(
    "strategy, unified_response",
    [
        ("majority", [{"value": ["1"], "strategy": "majority"}]),
        (
            "disagreement",
            [
                {"value": ["1"], "strategy": "disagreement"},
                {"value": ["1", "2"], "strategy": "disagreement"},
                {"value": ["1"], "strategy": "disagreement"},
            ],
        ),
    ],
)
def test_multi_label_question_strategy(strategy, unified_response):
    question_name = "rating"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": ["1"]}}},
            {"values": {question_name: {"value": ["1", "2"]}}},
            {"values": {question_name: {"value": ["1"]}}},
        ],
    }
    record = FeedbackRecord(**records_payload)
    question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "labels": ["1", "2"],
    }
    question = MultiLabelQuestion(**question_payload)
    strategy = MultiLabelQuestionStrategy(strategy)
    strategy.unify_responses([record], question)
    unified_response = [UnificatiedValueSchema(**resp) for resp in unified_response]
    assert record._unified_responses[question_name] == unified_response
    assert MultiLabelQuestionUnification(question=question, strategy=strategy)


def test_label_question_strategy_not_implemented():
    with pytest.raises(NotImplementedError, match="'majority_weighted'-strategy not implemented yet"):
        LabelQuestionStrategy._majority_weighted("mock", "mock")

    with pytest.raises(NotImplementedError, match="'majority_weighted'-strategy not implemented yet"):
        MultiLabelQuestionStrategy._majority_weighted("mock", "mock")
