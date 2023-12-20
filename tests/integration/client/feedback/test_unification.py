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
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
)
from argilla.client.feedback.unification import (
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

responses_rating = [
    {"values": {"rating": {"value": "1"}}},
    {"values": {"rating": {"value": "2"}}},
    {"values": {"rating": {"value": "2"}}},
]

responses_rating_equal = [
    {"values": {"rating": {"value": "2"}}},
    {"values": {"rating": {"value": "2"}}},
]


@pytest.mark.parametrize(
    "strategy, unified_response, responses",
    [
        ("mean", [{"value": str(int(5 / 3)), "strategy": "mean"}], responses_rating),
        ("majority", [{"value": "2", "strategy": "majority"}], responses_rating),
        ("max", [{"value": "2", "strategy": "max"}], responses_rating),
        ("min", [{"value": "1", "strategy": "min"}], responses_rating),
        ("mean", [{"value": str(2), "strategy": "mean"}], responses_rating_equal),
        ("majority", [{"value": "2", "strategy": "majority"}], responses_rating_equal),
        ("max", [{"value": "2", "strategy": "max"}], responses_rating_equal),
        ("min", [{"value": "2", "strategy": "min"}], responses_rating_equal),
    ],
)
def test_rating_question_strategy(strategy, unified_response, responses):
    question_name = "rating"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": responses,
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


responses_ranking = [
    {"values": {"ranking": {"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}]}}},
    {"values": {"ranking": {"value": [{"rank": 2, "value": "yes"}, {"rank": 1, "value": "no"}]}}},
    {"values": {"ranking": {"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}]}}},
]

responses_ranking_equal = [
    {"values": {"ranking": {"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}]}}},
    {"values": {"ranking": {"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}]}}},
]


@pytest.mark.parametrize(
    "strategy, unified_response, responses",
    [
        (
            "majority",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "majority"}],
            responses_ranking,
        ),
        (
            "max",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "max"}],
            responses_ranking,
        ),
        (
            "min",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 1, "value": "no"}], "strategy": "min"}],
            responses_ranking,
        ),
        (
            "mean",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 2, "value": "no"}], "strategy": "mean"}],
            responses_ranking,
        ),
        (
            "majority",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "majority"}],
            responses_ranking_equal,
        ),
        (
            "max",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "max"}],
            responses_ranking_equal,
        ),
        (
            "min",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "min"}],
            responses_ranking_equal,
        ),
        (
            "mean",
            [{"value": [{"rank": 2, "value": "yes"}, {"rank": 3, "value": "no"}], "strategy": "mean"}],
            responses_ranking_equal,
        ),
    ],
)
def test_ranking_question_strategy(strategy, unified_response, responses):
    question_name = "ranking"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": responses,
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


responses_label = [
    {"values": {"label": {"value": "1"}}},
    {"values": {"label": {"value": "2"}}},
    {"values": {"label": {"value": "2"}}},
]

responses_label_equal = [
    {"values": {"label": {"value": "2"}}},
    {"values": {"label": {"value": "2"}}},
]

responses_label_different = [
    {"values": {"label": {"value": "1"}}},
    {"values": {"label": {"value": "2"}}},
]


@pytest.mark.parametrize(
    "strategy, unified_response, responses",
    [
        ("majority", [{"value": "2", "strategy": "majority"}], responses_label),
        (
            "disagreement",
            [
                {"value": "1", "strategy": "disagreement"},
                {"value": "2", "strategy": "disagreement"},
                {"value": "2", "strategy": "disagreement"},
            ],
            responses_label,
        ),
        ("majority", [{"value": "2", "strategy": "majority"}], responses_label_equal),
        (
            "disagreement",
            [
                {"value": "2", "strategy": "disagreement"},
                {"value": "2", "strategy": "disagreement"},
            ],
            responses_label_equal,
        ),
        ("majority", [{"value": "1", "strategy": "majority"}], responses_label_different),
        (
            "disagreement",
            [
                {"value": "1", "strategy": "disagreement"},
                {"value": "2", "strategy": "disagreement"},
            ],
            responses_label_different,
        ),
    ],
)
def test_label_question_strategy(strategy, unified_response, responses):
    # To ensure reproducibility for the cases that the answer must be chosen randomly
    import random

    random.seed(42)

    question_name = "label"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": responses,
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


responses_multilabel = [
    {"values": {"multilabel": {"value": ["label1"]}}},
    {"values": {"multilabel": {"value": ["label1", "label2"]}}},
    {"values": {"multilabel": {"value": ["label1"]}}},
]

responses_multilabel_equal = [
    {"values": {"multilabel": {"value": ["label1"]}}},
    {"values": {"multilabel": {"value": ["label2"]}}},
]


@pytest.mark.parametrize(
    "strategy, unified_response, responses",
    [
        ("majority", [{"value": ["label1"], "strategy": "majority"}], responses_multilabel),
        (
            "disagreement",
            [
                {"value": ["label1"], "strategy": "disagreement"},
                {"value": ["label1", "label2"], "strategy": "disagreement"},
                {"value": ["label1"], "strategy": "disagreement"},
            ],
            responses_multilabel,
        ),
        ("majority", [{"value": ["label1"], "strategy": "majority"}], responses_multilabel_equal),
        (
            "disagreement",
            [{"value": ["label1"], "strategy": "disagreement"}, {"value": ["label2"], "strategy": "disagreement"}],
            responses_multilabel_equal,
        ),
    ],
)
def test_multi_label_question_strategy(strategy, unified_response, responses):
    # To ensure reproducibility for the cases that the answer must be chosen randomly
    import random

    random.seed(42)

    question_name = "multilabel"
    records_payload = {
        "fields": {"text": "This is the first record", "label": "positive"},
        "responses": [
            {"values": {question_name: {"value": ["label1"]}}},
            {"values": {question_name: {"value": ["label1"]}}},
            {"values": {question_name: {"value": ["label2"]}}},
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


def test_label_question_strategy_not_implemented():
    with pytest.raises(NotImplementedError, match="'majority_weighted'-strategy not implemented yet"):
        LabelQuestionStrategy._majority_weighted("mock", "mock")

    with pytest.raises(NotImplementedError, match="'majority_weighted'-strategy not implemented yet"):
        MultiLabelQuestionStrategy._majority_weighted("mock", "mock")
