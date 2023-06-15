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
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    LabelQuestionStrategy,
    LabelQuestionUnification,
    MultiLabelQuestion,
    MultiLabelQuestionStrategy,
    MultiLabelQuestionUnification,
    RatingQuestion,
    RatingQuestionStrategy,
    RatingQuestionUnification,
    UnificatiedValueSchema,
)


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
    rating_records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": "1"}}},
            {"values": {question_name: {"value": "2"}}},
            {"values": {question_name: {"value": "2"}}},
        ],
    }
    record = FeedbackRecord(**rating_records_payload)
    rating_question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "values": ["1", "2"],
    }
    question = RatingQuestion(**rating_question_payload)
    strategy = RatingQuestionStrategy(strategy)
    strategy.unify_responses([record], question)
    unified_response = [UnificatiedValueSchema(**resp) for resp in unified_response]
    assert record.unified_responses[question_name] == unified_response
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
    rating_records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": "1"}}},
            {"values": {question_name: {"value": "2"}}},
            {"values": {question_name: {"value": "2"}}},
        ],
    }
    record = FeedbackRecord(**rating_records_payload)
    rating_question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "labels": ["1", "2"],
    }
    question = LabelQuestion(**rating_question_payload)
    strategy = LabelQuestionStrategy(strategy)
    strategy.unify_responses([record], question)
    unified_response = [UnificatiedValueSchema(**resp) for resp in unified_response]
    assert record.unified_responses[question_name] == unified_response
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
    rating_records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": ["1"]}}},
            {"values": {question_name: {"value": ["1", "2"]}}},
            {"values": {question_name: {"value": ["1"]}}},
        ],
    }
    record = FeedbackRecord(**rating_records_payload)
    rating_question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "labels": ["1", "2"],
    }
    question = MultiLabelQuestion(**rating_question_payload)
    strategy = MultiLabelQuestionStrategy(strategy)
    strategy.unify_responses([record], question)
    unified_response = [UnificatiedValueSchema(**resp) for resp in unified_response]
    assert record.unified_responses[question_name] == unified_response
    assert MultiLabelQuestionUnification(question=question, strategy=strategy)


def test_label_question_strategy_not_implemented():
    with pytest.raises(NotImplementedError):
        LabelQuestionStrategy._majority_weighted("mock", "mock")

    with pytest.raises(NotImplementedError):
        MultiLabelQuestionStrategy._majority_weighted("mock", "mock")
