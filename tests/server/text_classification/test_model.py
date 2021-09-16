#  coding=utf-8
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
from pydantic import ValidationError
from rubrix.server.tasks.commons import TaskStatus
from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.tasks.text_classification.api import (
    ClassPrediction,
    PredictionStatus,
    TextClassificationAnnotation,
    TextClassificationRecord,
)


def test_flatten_metadata():
    data = {
        "inputs": {"text": "bogh"},
        "metadata": {
            "mail": {"subject": "The mail subject", "body": "This is a large text body"}
        },
    }
    record = TextClassificationRecord.parse_obj(data)
    assert list(record.metadata.keys()) == ["mail.subject", "mail.body"]


def test_too_long_metadata():
    record = TextClassificationRecord.parse_obj(
        {
            "inputs": {"text": "bogh"},
            "metadata": {"too_long": "a"*1000},
        }
    )

    assert len(record.metadata["too_long"]) == MAX_KEYWORD_LENGTH


def test_too_long_label():
    with pytest.raises(ValidationError, match="exceeds max length"):
        TextClassificationRecord.parse_obj(
            {
                "inputs": {"text": "bogh"},
                "prediction": {
                    "agent": "test",
                    "labels": [{"class": "a"*1000}],
                },
            }
        )


def test_score_integrity():
    data = {
        "multi_label": False,
        "inputs": {"data": "My cool data"},
        "prediction": {
            "agent": "test",
            "labels": [
                {"class": "A", "score": 0.3},
                {"class": "B", "score": 0.9},
            ],
        },
    }

    try:
        TextClassificationRecord.parse_obj(data)
    except ValidationError as e:
        assert "Wrong score distributions" in e.json()

    data["multi_label"] = True
    record = TextClassificationRecord.parse_obj(data)
    assert record is not None

    data["multi_label"] = False
    data["prediction"]["labels"] = [
        {"class": "B", "score": 0.9},
    ]
    record = TextClassificationRecord.parse_obj(data)
    assert record is not None

    data["prediction"]["labels"] = [
        {"class": "B", "score": 0.10000000012},
        {"class": "B", "score": 0.90000000002},
    ]
    record = TextClassificationRecord.parse_obj(data)
    assert record is not None


def test_prediction_ok_cases():

    data = {
        "multi_label": True,
        "inputs": {"data": "My cool data"},
        "prediction": {
            "agent": "test",
            "labels": [
                {"class": "A", "score": 0.3},
                {"class": "B", "score": 0.9},
            ],
        },
    }

    record = TextClassificationRecord(**data)
    assert record.predicted is None
    record.annotation = TextClassificationAnnotation(
        **{
            "agent": "test",
            "labels": [
                {"class": "A", "score": 1},
                {"class": "B", "score": 1},
            ],
        },
    )
    assert record.predicted == PredictionStatus.KO

    record.prediction = TextClassificationAnnotation(
        **{
            "agent": "test",
            "labels": [
                {"class": "A", "score": 0.9},
                {"class": "B", "score": 0.9},
            ],
        },
    )
    assert record.predicted == PredictionStatus.OK

    record.prediction = None
    assert record.predicted is None


def test_score_ranges():
    with pytest.raises(ValidationError, match="less than or equal to 1.0"):
        ClassPrediction(class_label="BB", score=100)

    with pytest.raises(ValidationError, match="greater than or equal to 0.0"):
        ClassPrediction(class_label="BB", score=-100)


def test_predicted_as_with_no_labels():
    data = {
        "inputs": {"text": "The input text"},
        "prediction": {"agent": "test", "labels": []},
    }
    record = TextClassificationRecord(**data)
    assert record.predicted_as == []


def test_created_record_with_default_status():
    data = {
        "inputs": {"data": "My cool data"},
    }

    record = TextClassificationRecord.parse_obj(data)
    assert record.status == TaskStatus.default


def test_predicted_ok_for_multilabel_unordered():
    record = TextClassificationRecord(
        inputs={"text": "The text"},
        prediction=TextClassificationAnnotation(
            agent="test",
            labels=[
                ClassPrediction(class_label="B"),
                ClassPrediction(class_label="C", score=0.3),
                ClassPrediction(class_label="A"),
            ],
        ),
        annotation=TextClassificationAnnotation(
            agent="test",
            labels=[ClassPrediction(class_label="A"), ClassPrediction(class_label="B")],
        ),
        multi_label=True,
    )

    assert record.predicted == PredictionStatus.OK
