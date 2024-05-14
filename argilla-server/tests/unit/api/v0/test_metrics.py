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
from typing import TYPE_CHECKING

import pytest
from argilla_server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextRecord,
)
from argilla_server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
    TextClassificationRecord,
)
from argilla_server.apis.v0.models.token_classification import (
    TokenClassificationBulkRequest,
    TokenClassificationRecord,
)
from argilla_server.commons.models import TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User, UserRole
from argilla_server.services.metrics.models import CommonTasksMetrics
from argilla_server.services.tasks.text_classification.metrics import TextClassificationMetrics
from argilla_server.services.tasks.token_classification.metrics import TokenClassificationMetrics

from tests.factories import UserFactory, WorkspaceFactory

if TYPE_CHECKING:
    from httpx import AsyncClient

COMMON_METRICS_LENGTH = len(CommonTasksMetrics.metrics)
CLASSIFICATION_METRICS_LENGTH = len(TextClassificationMetrics.metrics)


@pytest.mark.asyncio
async def test_wrong_dataset_metrics(async_client: "AsyncClient"):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=UserRole.owner, workspaces=[workspace])

    async_client.headers.update({API_KEY_HEADER_NAME: user.api_key})
    workspace_query_params = {"workspace": workspace.name}

    records = [Text2TextRecord.parse_obj(data) for data in [{"text": "this is a text"}] * 4]
    request = Text2TextBulkRequest(records=records)
    dataset = "test_wrong_dataset_metrics"

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200
    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.text2text.value, "workspace": workspace.name},
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/Text2Text:bulk",
        json=request.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TokenClassification/{dataset}/metrics", params=workspace_query_params
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::WrongTaskError",
            "params": {"message": "Provided task TokenClassification cannot be applied to dataset"},
        }
    }

    response = await async_client.post(
        f"/api/datasets/TokenClassification/{dataset}/metrics/a-metric:summary",
        json={},
        params=workspace_query_params,
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::WrongTaskError",
            "params": {"message": "Provided task TokenClassification cannot be applied to dataset"},
        }
    }


@pytest.mark.asyncio
async def test_dataset_for_text2text(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    records = [Text2TextRecord.parse_obj(data) for data in [{"text": "this is a text"}] * 4]
    request = Text2TextBulkRequest(records=records)
    dataset = "test_dataset_for_text2text"

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200
    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.text2text.value, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200
    response = await async_client.post(
        f"/api/datasets/{dataset}/Text2Text:bulk",
        json=request.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/Text2Text/{dataset}/metrics",
        params=workspace_query_params,
    )
    assert response.status_code == 200

    metrics = response.json()
    assert len(metrics) == COMMON_METRICS_LENGTH


@pytest.mark.asyncio
async def test_dataset_for_token_classification(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

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

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200
    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.token_classification.value, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200
    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=request.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TokenClassification/{dataset}/metrics", params=workspace_query_params
    )
    assert response.status_code == 200

    metrics = response.json()
    assert len(metrics) == len(TokenClassificationMetrics.metrics)

    for metric in metrics:
        metric_id = metric["id"]

        response = await async_client.post(
            f"/api/datasets/TokenClassification/{dataset}/metrics/{metric_id}:summary",
            json={},
            params=workspace_query_params,
        )

        assert response.status_code == 200, f"{metric} :: {response.json()}"
        summary = response.json()

        if "length" not in metric_id and "predicted" not in metric_id and "annotated" not in metric_id:
            assert summary, (metric_id, summary)


@pytest.mark.asyncio
async def test_dataset_metrics(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

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

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification.value, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=request.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/metrics", params=workspace_query_params
    )
    assert response.status_code == 200

    metrics = response.json()
    assert len(metrics) == CLASSIFICATION_METRICS_LENGTH

    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/metrics/missing_metric:summary",
        json={},
        params=workspace_query_params,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::EntityNotFoundError",
            "params": {"name": "missing_metric", "type": "ServiceBaseMetric"},
        }
    }

    for metric in metrics:
        response = await async_client.post(
            f"/api/datasets/TextClassification/{dataset}/metrics/{metric['id']}:summary",
            json={},
            params=workspace_query_params,
        )
        assert response.status_code == 200, f"{metric}: {response.json()}"


async def create_some_classification_data(
    async_client: "AsyncClient", dataset: str, workspace_name: str, records: list
):
    workspace_query_params = {"workspace": workspace_name}

    request = TextClassificationBulkRequest(records=[TextClassificationRecord.parse_obj(r) for r in records])

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets", json={"name": dataset, "task": TaskType.text_classification.value, "workspace": workspace_name}
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=request.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_labeling_rule_metric(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_labeling_rule_metric"
    await create_some_classification_data(
        async_client,
        dataset,
        records=[{"inputs": {"text": "This is classification record"}}] * 10,
        workspace_name=argilla_user.username,
    )

    rule_query = "t*"
    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/metrics/labeling_rule:summary?rule_query={rule_query}",
        json={},
        params=workspace_query_params,
    )
    assert response.json() == {
        "annotated_covered_records": 0,
        "correct_records": 0,
        "covered_records": 10,
        "incorrect_records": 0,
    }


@pytest.mark.asyncio
async def test_dataset_labels_for_text_classification(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

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

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification.value, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=request.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/metrics/dataset_labels:summary",
        json={},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = response.json()
    labels = response["labels"]
    assert sorted(labels) == ["A", "B", "D", "E"]
