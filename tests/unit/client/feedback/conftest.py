from typing import List

import pytest

from argilla.feedback import (
    FeedbackRecord,
    TextField,
    TextQuestion,
    RatingQuestion,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
)


@pytest.fixture
def feedback_dataset_guidelines() -> str:
    return "These are the annotation guidelines."


@pytest.fixture
def feedback_dataset_fields() -> List["AllowedFieldTypes"]:
    return [
        TextField(name="text", required=True),
        TextField(name="label", required=True),
    ]


@pytest.fixture
def feedback_dataset_questions() -> List["AllowedQuestionTypes"]:
    return [
        TextQuestion(name="question-1", required=True),
        RatingQuestion(name="question-2", values=[1, 2], required=True),
        LabelQuestion(name="question-3", labels=["a", "b", "c"], required=True),
        MultiLabelQuestion(name="question-4", labels=["a", "b", "c"], required=True),
        RankingQuestion(name="question-5", values=["a", "b"], required=True),
    ]


@pytest.fixture
def feedback_dataset_records() -> List[FeedbackRecord]:
    return [
        FeedbackRecord(
            fields={"text": "This is a positive example", "label": "positive"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "a"},
                        "question-4": {"value": ["a", "b"]},
                        "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                    },
                    "status": "submitted",
                },
            ],
            metadata={"unit": "test"},
            external_id="1",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            metadata={"another unit": "test"},
            external_id="2",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "b"},
                        "question-4": {"value": ["b", "c"]},
                        "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                    },
                    "status": "submitted",
                }
            ],
            suggestions=[
                {
                    "question_name": "question-1",
                    "value": "This is a suggestion to question 1",
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-2",
                    "value": 1,
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-3",
                    "value": "a",
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-4",
                    "value": ["a", "b"],
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-5",
                    "value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}],
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
            ],
            external_id="3",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "c"},
                        "question-4": {"value": ["a", "c"]},
                        "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                    },
                    "status": "submitted",
                }
            ],
            external_id="4",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "a"},
                        "question-4": {"value": ["a"]},
                        "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                    },
                    "status": "submitted",
                }
            ],
            external_id="5",
        ),
    ]


@pytest.fixture
def rating_question_payload():
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "values": ["1", "2"],
    }


@pytest.fixture
def label_question_payload():
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "labels": ["1", "2"],
    }


@pytest.fixture
def ranking_question_payload():
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "values": ["1", "2"],
    }
