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
from argilla_server.apis.v0.models.text_classification import (
    CreateLabelingRule,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkRequest,
    TextClassificationRecord,
)
from argilla_server.commons.models import TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User

if TYPE_CHECKING:
    from httpx import AsyncClient


async def log_some_records(
    client: "AsyncClient",
    dataset: str,
    workspace_name: str,
    annotation: str = None,
    multi_label: bool = False,
    delete: bool = True,
):
    if delete:
        response = await client.delete(f"/api/datasets/{dataset}", params={"workspace": workspace_name})
        assert response.status_code == 200

        response = await client.post(
            "/api/datasets",
            json={"name": dataset, "task": TaskType.text_classification.value, "workspace": workspace_name},
        )
        assert response.status_code == 200, response.json()

    record = {
        "id": 0,
        "inputs": {"text": "Esto es un ejemplo de texto"},
        "metadata": {"field.one": 1, "field.two": 2},
        "multi_label": multi_label,
    }

    if annotation:
        record["annotation"] = {"agent": "test", "labels": [{"class": annotation}]}

    response = await client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(records=[TextClassificationRecord(**record)]).dict(by_alias=True),
        params={"workspace": workspace_name},
    )
    assert response.status_code == 200, response.json()


@pytest.mark.asyncio
async def test_dataset_without_rules(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_dataset_without_rules"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username)

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", params=workspace_query_params
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_dataset_update_rule(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_dataset_with_rules"
    query = "a query"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username)

    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(query=query, label="LALA").dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.patch(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{query}",
        json={"label": "NEW Label"},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", params=workspace_query_params
    )
    assert response.status_code == 200

    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0].label == "NEW Label"
    assert rules[0].labels == ["NEW Label"]
    assert rules[0].description is None

    response = await async_client.patch(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{query}",
        json={"labels": ["A", "B"], "description": "New description"},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", params=workspace_query_params
    )
    assert response.status_code == 200

    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0].description == "New description"
    assert rules[0].label is None
    assert rules[0].labels == ["A", "B"]


@pytest.mark.parametrize(
    "rule",
    [
        CreateLabelingRule(query="a query", description="Description", label="LALA"),
        CreateLabelingRule(query="/a qu?ry/", description="Description", label="LALA"),
        CreateLabelingRule(query="another query", description="Description", labels=["A", "B", "C"]),
    ],
)
@pytest.mark.asyncio
async def test_dataset_with_rules(async_client: "AsyncClient", argilla_user: User, rule: CreateLabelingRule):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_dataset_with_rules"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username)

    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", json=rule.dict(), params=workspace_query_params
    )
    assert response.status_code == 200

    created_rule = LabelingRule.parse_obj(response.json())
    assert created_rule.query == rule.query
    assert created_rule.label == rule.label
    assert created_rule.labels == rule.labels
    assert created_rule.description == rule.description

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", params=workspace_query_params
    )
    assert response.status_code == 200

    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0] == created_rule


@pytest.mark.parametrize(
    "rule",
    [
        CreateLabelingRule(query="a query", description="Description", label="LALA"),
        CreateLabelingRule(query="/a qu(e|E)ry/", description="Description", label="LALA"),
        CreateLabelingRule(query="another query", description="Description", labels=["A", "B", "C"]),
    ],
)
@pytest.mark.asyncio
async def test_get_dataset_rule(async_client: "AsyncClient", argilla_user: User, rule: CreateLabelingRule):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_get_dataset_rule"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username)

    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{rule.query}", params=workspace_query_params
    )
    assert response.status_code == 200

    found_rule = LabelingRule.parse_obj(response.json())
    assert found_rule.query == rule.query
    assert found_rule.label == rule.label
    assert found_rule.labels == rule.labels
    assert found_rule.description == rule.description


@pytest.mark.asyncio
async def test_delete_dataset_rules(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_delete_dataset_rules"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username)

    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(query="/a query/", label="TEST", description="Description").dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.delete(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules//a query/", params=workspace_query_params
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", params=workspace_query_params
    )
    assert response.status_code == 200

    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_duplicated_dataset_rules(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_duplicated_dataset_rules"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username)

    rule = CreateLabelingRule(query="a query", labels=["TEST"])
    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", json=rule.dict(), params=workspace_query_params
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::EntityAlreadyExistsError",
            "params": {"name": "a query", "type": "ServiceLabelingRule"},
        }
    }


@pytest.mark.asyncio
async def test_rules_with_multi_label_dataset(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_rules_with_multi_label_dataset"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, multi_label=True)

    rule = CreateLabelingRule(query="a query", description="Description", label="LALA")
    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", json=rule.dict(), params=workspace_query_params
    )
    assert response.status_code == 200

    found_rule = LabelingRule.parse_obj(response.json())
    assert found_rule.query == rule.query
    assert found_rule.label == rule.label
    assert found_rule.labels == rule.labels
    assert found_rule.description == rule.description


@pytest.mark.asyncio
async def test_rule_metrics_with_missing_label(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_rule_metrics_with_missing_label"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation="OK")

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/a query/metrics", params=workspace_query_params
    )
    assert response.status_code == 200, response.json()

    assert response.json() == {
        "coverage": 0.0,
        "coverage_annotated": 0.0,
        "correct": 0.0,
        "incorrect": 0.0,
        "total_records": 1,
        "annotated_records": 1,
    }


@pytest.mark.parametrize(
    ("rule", "expected_metrics"),
    [
        (
            CreateLabelingRule(query="ejemplo", label="TEST"),
            {
                "annotated_records": 1,
                "correct": 0.0,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "incorrect": 1.0,
                "precision": 0.0,
                "total_records": 1,
            },
        ),
        (
            CreateLabelingRule(query="ejemplo", label="test.bad"),
            {
                "annotated_records": 1,
                "correct": 0.0,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "incorrect": 1.0,
                "precision": 0.0,
                "total_records": 1,
            },
        ),
        (
            CreateLabelingRule(query="ejemplo", label="o.k."),
            {
                "annotated_records": 1,
                "correct": 1.0,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "incorrect": 0.0,
                "precision": 1.0,
                "total_records": 1,
            },
        ),
        (
            CreateLabelingRule(query="bad query", label="TEST"),
            {
                "annotated_records": 1,
                "correct": 0.0,
                "coverage": 0.0,
                "coverage_annotated": 0.0,
                "incorrect": 0.0,
                "total_records": 1,
            },
        ),
        (
            CreateLabelingRule(query="ejemplo", labels=["TEST", "A", "B"]),
            {
                "annotated_records": 1,
                "correct": 0.0,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "incorrect": 3.0,
                "precision": 0.0,
                "total_records": 1,
            },
        ),
        (
            CreateLabelingRule(query="ejemplo", labels=["A", "o.k."]),
            {
                "annotated_records": 1,
                "correct": 1.0,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "incorrect": 1.0,
                "precision": 0.5,
                "total_records": 1,
            },
        ),
        (
            CreateLabelingRule(query="/eje.*o/", labels=["A", "o.k."]),
            {
                "annotated_records": 1,
                "correct": 1.0,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "incorrect": 1.0,
                "precision": 0.5,
                "total_records": 1,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_rule_metrics_with_missing_label_for_stored_rule(
    async_client: "AsyncClient", argilla_user: User, rule, expected_metrics
):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_rule_metrics_with_missing_label_for_stored_rule"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation="o.k.")
    response = await async_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", json=rule.dict(), params=workspace_query_params
    )
    assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{rule.query}/metrics", params=workspace_query_params
    )
    assert response.status_code == 200

    assert response.json() == expected_metrics


@pytest.mark.asyncio
async def test_create_rules_and_then_log(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_create_rules_and_then_log"

    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation="OK")
    for query in ["ejemplo", "bad query"]:
        response = await async_client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(query=query, label="TEST", description="Description").dict(),
            params=workspace_query_params,
        )
        assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", params=workspace_query_params
    )
    assert response.status_code == 200

    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 2

    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation="OK", delete=False)
    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", params=workspace_query_params
    )
    assert response.status_code == 200

    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 2


@pytest.mark.parametrize(
    ("rules", "expected_metrics", "annotation"),
    [
        (
            [
                CreateLabelingRule(query="ejemplo", label="TEST"),
                CreateLabelingRule(query="bad request", label="TEST"),
                CreateLabelingRule(query="other", labels=["A", "B"]),
            ],
            {
                "annotated_records": 1,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "total_records": 1,
            },
            "OK",
        ),
        (
            [
                CreateLabelingRule(query="/eje.?plo/", label="TEST"),
                CreateLabelingRule(query="bad request", label="TEST"),
                CreateLabelingRule(query="other", labels=["A", "B"]),
            ],
            {
                "annotated_records": 0,
                "coverage": 1.0,
                "total_records": 1,
            },
            None,
        ),
        (
            [
                CreateLabelingRule(query="ejemplo", label="TEST"),
                CreateLabelingRule(query="bad request", label="bad.label"),
                CreateLabelingRule(query="other", labels=["A", "B", "good.label"]),
            ],
            {
                "annotated_records": 1,
                "coverage": 1.0,
                "coverage_annotated": 1.0,
                "total_records": 1,
            },
            "good.label",
        ),
    ],
)
@pytest.mark.asyncio
async def test_dataset_rules_metrics(
    async_client: "AsyncClient", argilla_user: User, rules, expected_metrics, annotation
):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_dataset_rules_metrics"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation=annotation)

    for rule in rules:
        response = await async_client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=rule.dict(),
            params=workspace_query_params,
        )
        assert response.status_code == 200

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/metrics", params=workspace_query_params
    )
    assert response.status_code == 200, response.json()

    assert response.json() == expected_metrics


@pytest.mark.asyncio
async def test_rule_metric(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_rule_metric"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation="OK")

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics?label=TEST",
        params=workspace_query_params,
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.total_records == 1
    assert metrics.coverage == 1
    assert metrics.coverage_annotated == 1
    assert metrics.correct == 0
    assert metrics.incorrect == 1
    assert metrics.precision == 0

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics?label=OK",
        params=workspace_query_params,
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.correct == 1
    assert metrics.incorrect == 0
    assert metrics.precision == 1

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics", params=workspace_query_params
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.correct == 0
    assert metrics.incorrect == 0
    assert metrics.precision is None
    assert metrics.coverage_annotated == 1

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/badd/metrics?label=OK",
        params=workspace_query_params,
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.total_records == 1
    assert metrics.coverage == 0
    assert metrics.coverage_annotated == 0
    assert metrics.correct == 0
    assert metrics.incorrect == 0
    assert metrics.precision is None


@pytest.mark.asyncio
async def test_rule_metric_with_multiple_labels(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_rule_metric"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation="OK")

    response = await async_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics?label=A&label=OK",
        params=workspace_query_params,
    )
    assert response.status_code == 200

    assert response.json() == {
        "annotated_records": 1,
        "correct": 1.0,
        "coverage": 1.0,
        "coverage_annotated": 1.0,
        "incorrect": 1.0,
        "precision": 0.5,
        "total_records": 1,
    }


@pytest.mark.asyncio
async def test_search_records_with_uncovered_rules(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_search_records_with_uncovered_rules"
    await log_some_records(async_client, dataset, workspace_name=argilla_user.username, annotation="OK")

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search", params=workspace_query_params
    )
    assert response.status_code == 200

    assert len(response.json()["records"]) == 1

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json={"query": {"uncovered_by_rules": ["texto"]}},
        params=workspace_query_params,
    )
    assert response.status_code == 200
    assert len(response.json()["records"]) == 0
