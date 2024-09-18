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
from argilla_v1.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
)
from argilla_v1.client.feedback.unification import (
    LabelQuestionStrategy,
    LabelQuestionUnification,
    MultiLabelQuestionStrategy,
    MultiLabelQuestionUnification,
    RankingQuestionStrategy,
    RankingQuestionUnification,
    RatingQuestionStrategy,
    RatingQuestionUnification,
    UnifiedValueSchema,
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
    strategy.compute_unified_responses([record], question)
    unified_response = [UnifiedValueSchema(**resp) for resp in unified_response]
    assert record._unified_responses[question_name] == unified_response
    assert RatingQuestionUnification(question=question, strategy=strategy)


@pytest.mark.parametrize(
    "strategy, unified_response",
    [
        ("majority", [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "majority"}]),
        ("max", [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "max"}]),
        ("min", [{"value": [{"rank": 2, "value": "yes"}, {"rank": 1, "value": "no"}], "strategy": "min"}]),
        ("mean", [{"value": [{"rank": 2, "value": "yes"}, {"rank": 2, "value": "no"}], "strategy": "mean"}]),
    ],
)
def test_ranking_question_strategy(strategy, unified_response):
    question_name = "ranking"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}]}}},
            {"values": {question_name: {"value": [{"rank": 2, "value": "yes"}, {"rank": 1, "value": "no"}]}}},
            {"values": {question_name: {"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}]}}},
        ],
    }
    record = FeedbackRecord(**records_payload)
    question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "values": ["yes", "no", "maybe"],
    }
    question = RankingQuestion(**question_payload)
    strategy = RankingQuestionStrategy(strategy)
    strategy.compute_unified_responses([record], question)
    unified_response = [UnifiedValueSchema(**resp) for resp in unified_response]
    assert record._unified_responses[question_name] == unified_response
    assert RankingQuestionUnification(question=question, strategy=strategy)


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
    strategy.compute_unified_responses([record], question)
    unified_response = [UnifiedValueSchema(**resp) for resp in unified_response]
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
    strategy.compute_unified_responses([record], question)
    unified_response = [UnifiedValueSchema(**resp) for resp in unified_response]
    assert record._unified_responses[question_name] == unified_response
    assert MultiLabelQuestionUnification(question=question, strategy=strategy)


@pytest.mark.parametrize(
    "strategy, unified_response",
    [
        ("majority", [{"value": ["label1"], "strategy": "majority"}]),
    ],
)
def test_multi_label_question_strategy_without_overlap(strategy, unified_response):
    question_name = "rating"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": ["label1"]}}},
            {"values": {question_name: {"value": ["label2"]}}},
        ],
    }
    record = FeedbackRecord(**records_payload)
    question_payload = {
        "name": question_name,
        "description": question_name,
        "required": True,
        "labels": ["label1", "label2"],
    }
    question = MultiLabelQuestion(**question_payload)
    strategy = MultiLabelQuestionStrategy(strategy)
    strategy.compute_unified_responses([record], question)
    unified_response = [UnifiedValueSchema(**resp) for resp in unified_response]
    assert record._unified_responses[question_name] == unified_response
    assert MultiLabelQuestionUnification(question=question, strategy=strategy)


def test_label_question_strategy_not_implemented():
    with pytest.raises(NotImplementedError, match="'majority_weighted'-strategy not implemented yet"):
        LabelQuestionStrategy._majority_weighted("mock", "mock")

    with pytest.raises(NotImplementedError, match="'majority_weighted'-strategy not implemented yet"):
        MultiLabelQuestionStrategy._majority_weighted("mock", "mock")
