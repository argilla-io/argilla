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
from argilla_server.apis.v0.models.text_classification import (
    TextClassificationAnnotation,
    TextClassificationQuery,
    TextClassificationRecord,
)
from argilla_server.commons.models import PredictionStatus, TaskStatus
from argilla_server.daos.backend.search.query_builder import EsQueryBuilder
from argilla_server.services.tasks.text_classification.model import (
    ClassPrediction,
    ServiceTextClassificationRecord,
)

from tests.pydantic_v1 import ValidationError


def test_flatten_metadata():
    data = {
        "inputs": {"text": "bogh"},
        "metadata": {"mail": {"subject": "The mail subject", "body": "This is a large text body"}},
    }
    record = ServiceTextClassificationRecord.parse_obj(data)
    assert list(record.metadata.keys()) == ["mail.subject", "mail.body"]


def test_metadata_with_object_list():
    data = {
        "inputs": {"text": "bogh"},
        "metadata": {
            "mails": [
                {"subject": "Mail One", "body": "This is a large text body"},
                {"subject": "Mail Two", "body": "This is a large text body"},
            ]
        },
    }
    record = ServiceTextClassificationRecord.parse_obj(data)
    assert list(record.metadata.keys()) == ["mails"]


def test_model_dict():
    record = TextClassificationRecord.parse_obj(
        {
            "id": 1,
            "inputs": {"text": "This is a text"},
            "annotation": {
                "agent": "test",
                "labels": [{"class": "A"}, {"class": "B"}],
            },
            "multi_label": True,
        }
    )

    assert record.dict(exclude_none=True) == {
        "annotation": {
            "agent": "test",
            "labels": [
                {"class_label": "A", "score": 1.0},
                {"class_label": "B", "score": 1.0},
            ],
        },
        "annotations": {
            "test": {
                "labels": [
                    {"class_label": "A", "score": 1.0},
                    {"class_label": "B", "score": 1.0},
                ]
            }
        },
        "id": 1,
        "inputs": {"text": "This is a text"},
        "metrics": {},
        "multi_label": True,
        "status": "Default",
    }


def test_model_with_annotations():
    record = TextClassificationRecord.parse_obj(
        {
            "annotations": {
                "test": {
                    "labels": [
                        {"class_label": "A", "score": 1.0},
                        {"class_label": "B", "score": 1.0},
                    ]
                }
            },
            "id": 1,
            "inputs": {"text": "This is a text"},
            "multi_label": True,
            "status": "Default",
        }
    )

    assert record.dict(exclude_none=True) == {
        "annotation": {
            "agent": "test",
            "labels": [
                {"class_label": "A", "score": 1.0},
                {"class_label": "B", "score": 1.0},
            ],
        },
        "annotations": {
            "test": {
                "labels": [
                    {"class_label": "A", "score": 1.0},
                    {"class_label": "B", "score": 1.0},
                ]
            }
        },
        "id": 1,
        "inputs": {"text": "This is a text"},
        "metrics": {},
        "multi_label": True,
        "status": "Default",
    }


def test_single_label_with_multiple_annotation():
    with pytest.raises(
        ValidationError,
        match="Single label record must include only one annotation label",
    ):
        ServiceTextClassificationRecord.parse_obj(
            {
                "inputs": {"text": "This is a text"},
                "annotation": {
                    "agent": "test",
                    "labels": [{"class": "A"}, {"class": "B"}],
                },
                "multi_label": False,
            }
        )


def test_too_long_metadata():
    record = ServiceTextClassificationRecord.parse_obj(
        {
            "inputs": {"text": "bogh"},
            "metadata": {"too_long": "a" * 1000},
        }
    )

    assert len(record.metadata["too_long"]) == 128


def test_too_long_label():
    with pytest.raises(ValidationError, match="exceeds max length"):
        ServiceTextClassificationRecord.parse_obj(
            {
                "inputs": {"text": "bogh"},
                "prediction": {
                    "agent": "test",
                    "labels": [{"class": "a" * 1000}],
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
        ServiceTextClassificationRecord.parse_obj(data)
    except ValidationError as e:
        assert "Wrong score distributions" in e.json()

    data["multi_label"] = True
    record = ServiceTextClassificationRecord.parse_obj(data)
    assert record is not None

    data["multi_label"] = False
    data["prediction"]["labels"] = [
        {"class": "B", "score": 0.9},
    ]
    record = ServiceTextClassificationRecord.parse_obj(data)
    assert record is not None

    data["prediction"]["labels"] = [
        {"class": "B", "score": 0.10000000012},
        {"class": "B", "score": 0.90000000002},
    ]
    record = ServiceTextClassificationRecord.parse_obj(data)
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

    record = ServiceTextClassificationRecord(**data)
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
    record = ServiceTextClassificationRecord(**data)
    assert record.predicted_as == []


def test_created_record_with_default_status():
    data = {
        "inputs": {"data": "My cool data"},
    }

    record = ServiceTextClassificationRecord.parse_obj(data)
    assert record.status == TaskStatus.default


def test_predicted_ok_for_multilabel_unordered():
    record = ServiceTextClassificationRecord(
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


@pytest.mark.parametrize(
    "annotation",
    [
        TextClassificationAnnotation(
            agent="test_ok",
            labels=[],
        ),
        None,
    ],
)
def test_validate_without_labels_for_single_label(annotation):
    with pytest.raises(
        ValidationError,
        match="Annotation must include some label for validated records",
    ):
        ServiceTextClassificationRecord(
            inputs={"text": "The text"},
            status=TaskStatus.validated,
            prediction=TextClassificationAnnotation(
                agent="test",
                labels=[
                    ClassPrediction(class_label="C", score=0.3),
                ],
            ),
            annotation=annotation,
        )


def test_query_with_uncovered_by_rules():
    query = TextClassificationQuery(uncovered_by_rules=["query", "other*"])

    assert EsQueryBuilder._to_es_query(query) == {
        "bool": {
            "must": {"match_all": {}},
            "must_not": {
                "bool": {
                    "minimum_should_match": 1,
                    "should": [
                        {
                            "bool": {
                                "must": {
                                    "query_string": {
                                        "default_field": "text",
                                        "default_operator": "AND",
                                        "query": "query",
                                    }
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": {
                                    "query_string": {
                                        "default_field": "text",
                                        "default_operator": "AND",
                                        "query": "other*",
                                    }
                                }
                            }
                        },
                    ],
                }
            },
        }
    }


def test_empty_labels_for_no_multilabel():
    with pytest.raises(
        ValidationError,
        match="Single label record must include only one annotation label",
    ):
        ServiceTextClassificationRecord(
            inputs={"text": "The input text"},
            annotation=TextClassificationAnnotation(agent="ann.", labels=[]),
        )

    record = ServiceTextClassificationRecord(
        inputs={"text": "The input text"},
        prediction=TextClassificationAnnotation(agent="ann.", labels=[]),
        annotation=TextClassificationAnnotation(agent="ann.", labels=[ClassPrediction(class_label="B")]),
    )
    assert record.predicted == PredictionStatus.KO


def test_annotated_without_labels_for_multilabel():
    record = ServiceTextClassificationRecord(
        inputs={"text": "The input text"},
        multi_label=True,
        prediction=TextClassificationAnnotation(agent="pred.", labels=[]),
        annotation=TextClassificationAnnotation(agent="ann.", labels=[]),
    )

    assert record.predicted == PredictionStatus.OK


def test_using_predictions_dict():
    record = ServiceTextClassificationRecord(
        inputs={"text": "this is a text"},
        predictions={
            "carl": TextClassificationAnnotation(agent="wat at", labels=[ClassPrediction(class_label="YES")]),
            "BOB": TextClassificationAnnotation(agent="wot wot", labels=[ClassPrediction(class_label="NO")]),
        },
    )

    assert record.prediction.dict() == {
        "agent": "carl",
        "labels": [{"class_label": "YES", "score": 1.0}],
    }
    assert record.predictions == {
        "BOB": TextClassificationAnnotation(labels=[ClassPrediction(class_label="NO")]),
        "carl": TextClassificationAnnotation(labels=[ClassPrediction(class_label="YES")]),
    }


def test_with_no_agent_at_all():
    with pytest.raises(ValidationError):
        ServiceTextClassificationRecord(
            inputs={"text": "this is a text"},
            prediction=TextClassificationAnnotation(labels=[ClassPrediction(class_label="YES")]),
        )
