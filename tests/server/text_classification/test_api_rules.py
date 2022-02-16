import pytest

from rubrix.server.commons.errors import EntityAlreadyExistsError
from rubrix.server.tasks.text_classification import (
    CreateLabelingRule,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
    TextClassificationRecord,
)


def log_some_records(
    client,
    dataset: str,
    annotation: str = None,
    multi_label: bool = False,
    delete: bool = True,
):
    if delete:
        assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    record = {
        "id": 0,
        "inputs": {"text": "Esto es un ejemplo de texto"},
        "metadata": {"field.one": 1, "field.two": 2},
        "multi_label": multi_label,
    }

    if annotation:
        record["annotation"] = {"agent": "test", "labels": [{"class": annotation}]}

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        data=TextClassificationBulkData(
            records=[
                TextClassificationRecord(**record),
            ],
        ).json(by_alias=True),
    )
    assert response.status_code == 200


def test_dataset_without_rules(mocked_client):
    dataset = "test_dataset_without_rules"
    log_some_records(mocked_client, dataset)

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_dataset_update_rule(mocked_client):
    dataset = "test_dataset_with_rules"
    query = "a query"
    log_some_records(mocked_client, dataset)

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(query=query, label="LALA").dict(),
    )
    assert response.status_code == 200

    mocked_client.patch(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{query}",
        json={"label": "NEW Label"},
    )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0].label == "NEW Label"
    assert rules[0].description is None

    mocked_client.patch(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{query}",
        json={"label": "NEW Label", "description": "New description"},
    )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0].description == "New description"


def test_dataset_with_rules(mocked_client):
    dataset = "test_dataset_with_rules"
    log_some_records(mocked_client, dataset)

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(
            query="a query", description="Description", label="LALA"
        ).dict(),
    )
    assert response.status_code == 200

    created_rule = LabelingRule.parse_obj(response.json())
    assert created_rule.query == "a query"
    assert created_rule.label == "LALA"
    assert created_rule.description == "Description"
    assert created_rule.author == "rubrix"

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    assert response.status_code == 200
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0] == created_rule


def test_get_dataset_rule(mocked_client):
    dataset = "test_get_dataset_rule"
    log_some_records(mocked_client, dataset)

    rule_query = "a query"
    rule_label = "TEST"
    rule_description = "Description"
    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(
            query=rule_query, label=rule_label, description=rule_description
        ).dict(),
    )
    assert response.status_code == 200

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{rule_query}"
    )
    assert response.status_code == 200
    rule = LabelingRule.parse_obj(response.json())
    assert rule.query == rule_query
    assert rule.label == rule_label
    assert rule.description == rule_description


def test_delete_dataset_rules(mocked_client):
    dataset = "test_delete_dataset_rules"
    log_some_records(mocked_client, dataset)

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(
            query="a query", label="TEST", description="Description"
        ).dict(),
    )
    assert response.status_code == 200

    response = mocked_client.delete(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{'a query'}"
    )
    assert response.status_code == 200

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_duplicated_dataset_rules(mocked_client):
    dataset = "test_duplicated_dataset_rules"
    log_some_records(mocked_client, dataset)

    rule = CreateLabelingRule(query="a query", label="TEST")
    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
    )
    assert response.status_code == 200

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": {
            "code": "rubrix.api.errors::EntityAlreadyExistsError",
            "params": {"name": "a query", "type": "LabelingRule"},
        }
    }


def test_rules_with_multi_label_dataset(mocked_client):
    dataset = "test_rules_with_multi_label_dataset"
    log_some_records(mocked_client, dataset, multi_label=True)

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(
            query="a query", description="Description", label="LALA"
        ).dict(),
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "rubrix.api.errors::BadRequestError",
            "params": {
                "message": "Labeling rules are not supported for multi-label datasets"
            },
        }
    }


def test_rule_metrics_with_missing_label(mocked_client):
    dataset = "test_rule_metrics_with_missing_label"
    log_some_records(mocked_client, dataset, annotation="OK")

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/a query/metrics"
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


def test_rule_metrics_with_missing_label_for_stored_rule(mocked_client):
    dataset = "test_rule_metrics_with_missing_label_for_stored_rule"
    log_some_records(mocked_client, dataset, annotation="OK")
    for query in ["ejemplo", "bad query"]:
        mocked_client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/bad query/metrics"
    )
    assert response.status_code == 200


def test_create_rules_and_then_log(mocked_client):
    dataset = "test_create_rules_and_then_log"
    log_some_records(mocked_client, dataset, annotation="OK")
    for query in ["ejemplo", "bad query"]:
        mocked_client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 2

    log_some_records(mocked_client, dataset, annotation="OK", delete=False)
    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 2


def test_dataset_rules_metrics(mocked_client):
    dataset = "test_dataset_rules_metrics"
    log_some_records(mocked_client, dataset, annotation="OK")

    for query in ["ejemplo", "bad query"]:
        mocked_client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/metrics"
    )
    assert response.status_code == 200, response.json()

    metrics = DatasetLabelingRulesMetricsSummary.parse_obj(response.json())
    assert metrics.coverage == 1
    assert metrics.coverage_annotated == 1
    assert metrics.total_records == 1
    assert metrics.annotated_records == 1


def test_dataset_rules_metrics_without_annotation(mocked_client):
    dataset = "test_dataset_rules_metrics_without_annotation"
    log_some_records(mocked_client, dataset)

    for query in ["ejemplo", "bad query"]:
        mocked_client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/metrics"
    )
    assert response.status_code == 200, response.json()

    metrics = DatasetLabelingRulesMetricsSummary.parse_obj(response.json())
    assert metrics.coverage == 1
    assert metrics.total_records == 1
    assert metrics.annotated_records == 0
    assert metrics.coverage_annotated is None


def test_rule_metric(mocked_client):
    dataset = "test_rule_metric"
    log_some_records(mocked_client, dataset, annotation="OK")

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics?label=TEST"
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.total_records == 1
    assert metrics.coverage == 1
    assert metrics.coverage_annotated == 1
    assert metrics.correct == 0
    assert metrics.incorrect == 1
    assert metrics.precision == 0

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics?label=OK"
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.correct == 1
    assert metrics.incorrect == 0
    assert metrics.precision == 1

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics"
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.correct == 0
    assert metrics.incorrect == 0
    assert metrics.precision is None
    assert metrics.coverage_annotated == 1

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/badd/metrics?label=OK"
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.total_records == 1
    assert metrics.coverage == 0
    assert metrics.coverage_annotated == 0
    assert metrics.correct == 0
    assert metrics.incorrect == 0
    assert metrics.precision is None


def test_search_records_with_uncovered_rules(mocked_client):
    dataset = "test_search_records_with_uncovered_rules"
    log_some_records(mocked_client, dataset, annotation="OK")

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
    )
    assert len(response.json()["records"]) == 1

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json={"query": {"uncovered_by_rules": ["texto"]}},
    )
    assert len(response.json()["records"]) == 0
