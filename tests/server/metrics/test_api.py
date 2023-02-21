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

from argilla.server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextRecord,
)
from argilla.server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
    TextClassificationRecord,
)
from argilla.server.apis.v0.models.token_classification import (
    TokenClassificationBulkRequest,
    TokenClassificationRecord,
)
from argilla.server.services.metrics.models import CommonTasksMetrics
from argilla.server.services.tasks.text_classification.metrics import (
    TextClassificationMetrics,
)
from argilla.server.services.tasks.token_classification.metrics import (
    TokenClassificationMetrics,
)

COMMON_METRICS_LENGTH = len(CommonTasksMetrics.metrics)
CLASSIFICATION_METRICS_LENGTH = len(TextClassificationMetrics.metrics)


def test_wrong_dataset_metrics(mocked_client):
    text = "This is a text"
    records = [
        Text2TextRecord.parse_obj(data)
        for data in [
            {"text": text},
            {"text": text},
            {"text": text},
            {"text": text},
        ]
    ]
    request = Text2TextBulkRequest(records=records)
    dataset = "test_wrong_dataset_metrics"

    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    assert (
        mocked_client.post(
            f"/api/datasets/{dataset}/Text2Text:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 200
    )

    response = mocked_client.get(f"/api/datasets/TokenClassification/{dataset}/metrics")
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::WrongTaskError",
            "params": {"message": "Provided task TokenClassification cannot be applied to dataset"},
        }
    }

    response = mocked_client.post(
        f"/api/datasets/TokenClassification/{dataset}/metrics/a-metric:summary",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::WrongTaskError",
            "params": {"message": "Provided task TokenClassification cannot be applied to dataset"},
        }
    }


def test_dataset_for_text2text(mocked_client):
    text = "This is a text"
    records = [
        Text2TextRecord.parse_obj(data)
        for data in [
            {"text": text},
            {"text": text},
            {"text": text},
            {"text": text},
        ]
    ]
    request = Text2TextBulkRequest(records=records)
    dataset = "test_dataset_for_text2text"

    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    assert (
        mocked_client.post(
            f"/api/datasets/{dataset}/Text2Text:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 200
    )

    metrics = mocked_client.get(f"/api/datasets/Text2Text/{dataset}/metrics").json()
    assert len(metrics) == COMMON_METRICS_LENGTH


def test_dataset_for_token_classification(mocked_client):
    text = "This is a contaminated text"
    metadata = {"metadata": {"field": 1}}
    prediction = {"prediction": {"entities": [], "agent": "test", "score": 0.3}}
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {"text": text, "tokens": text.split(" "), **metadata, **prediction},
            {"text": text, "tokens": text.split(" "), **metadata, **prediction},
            {"text": text, "tokens": text.split(" "), **metadata, **prediction},
            {"text": text, "tokens": text.split(" "), **metadata, **prediction},
        ]
    ]

    request = TokenClassificationBulkRequest(records=records)
    dataset = "test_dataset_for_token_classification"

    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200

    assert (
        mocked_client.post(
            f"/api/datasets/{dataset}/TokenClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 200
    )
    metrics = mocked_client.get(f"/api/datasets/TokenClassification/{dataset}/metrics").json()
    assert len(metrics) == len(TokenClassificationMetrics.metrics)

    for metric in metrics:
        metric_id = metric["id"]

        response = mocked_client.post(
            f"/api/datasets/TokenClassification/{dataset}/metrics/{metric_id}:summary",
            json={},
        )

        assert response.status_code == 200, f"{metric} :: {response.json()}"
        summary = response.json()

        if not ("predicted" in metric_id or "annotated" in metric_id):
            assert len(summary) > 0, (metric_id, summary)


def test_dataset_metrics(mocked_client):
    records = [
        TextClassificationRecord.parse_obj(data)
        for data in [
            {
                "id": 0,
                "inputs": {"text": "Some test data"},
                "multi_label": False,
                "metadata": {"textLength": len("Some test data")},
            },
            {
                "id": 1,
                "inputs": {"text": "Another data with different length"},
                "multi_label": False,
                "metadata": {"textLength": len("Another data with different length")},
            },
        ]
    ]
    request = TextClassificationBulkRequest(records=records)
    dataset = "test_get_dataset_metrics"

    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200

    assert (
        mocked_client.post(
            f"/api/datasets/{dataset}/TextClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 200
    )

    metrics = mocked_client.get(f"/api/datasets/TextClassification/{dataset}/metrics").json()

    assert len(metrics) == CLASSIFICATION_METRICS_LENGTH

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/metrics/missing_metric:summary",
        json={},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::EntityNotFoundError",
            "params": {"name": "missing_metric", "type": "ServiceBaseMetric"},
        }
    }

    for metric in metrics:
        response = mocked_client.post(
            f"/api/datasets/TextClassification/{dataset}/metrics/{metric['id']}:summary",
            json={},
        )
        assert response.status_code == 200, f"{metric}: {response.json()}"


def create_some_classification_data(mocked_client, dataset: str, records: list):
    request = TextClassificationBulkRequest(records=[TextClassificationRecord.parse_obj(r) for r in records])

    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    assert (
        mocked_client.post(
            f"/api/datasets/{dataset}/TextClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 200
    )


def test_labeling_rule_metric(mocked_client):
    dataset = "test_labeling_rule_metric"
    create_some_classification_data(
        mocked_client, dataset, records=[{"inputs": {"text": "This is classification record"}}] * 10
    )

    rule_query = "t*"
    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/metrics/labeling_rule:summary?rule_query={rule_query}",
        json={},
    )
    assert response.json() == {
        "annotated_covered_records": 0,
        "correct_records": 0,
        "covered_records": 10,
        "incorrect_records": 0,
    }


def test_dataset_labels_for_text_classification(mocked_client):
    records = [
        TextClassificationRecord.parse_obj(data)
        for data in [
            {
                "id": 0,
                "inputs": {"text": "Some test data"},
                "prediction": {"agent": "test", "labels": [{"class": "A"}]},
            },
            {
                "id": 1,
                "inputs": {"text": "Some test data"},
                "annotation": {"agent": "test", "labels": [{"class": "B"}]},
            },
            {
                "id": 2,
                "inputs": {"text": "Some test data"},
                "prediction": {
                    "agent": "test",
                    "labels": [
                        {"class": "A", "score": 0.5},
                        {
                            "class": "D",
                            "score": 0.5,
                        },
                    ],
                },
                "annotation": {"agent": "test", "labels": [{"class": "E"}]},
            },
        ]
    ]
    request = TextClassificationBulkRequest(records=records)
    dataset = "test_dataset_labels_for_text_classification"

    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200

    assert (
        mocked_client.post(
            f"/api/datasets/{dataset}/TextClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 200
    )

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/metrics/dataset_labels:summary",
        json={},
    )
    assert response.status_code == 200
    response = response.json()
    labels = response["labels"]
    assert sorted(labels) == ["A", "B", "D", "E"]
