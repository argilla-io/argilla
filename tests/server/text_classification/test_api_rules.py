import pytest

from rubrix.server.tasks.text_classification import (
    CreateLabelingRule,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
    TextClassificationRecord,
)
from tests.server.test_helpers import client


def log_some_records(
    dataset: str, annotation: str = None, multi_label: bool = False, delete: bool = True
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


def test_dataset_without_rules():
    dataset = "test_dataset_without_rules"
    log_some_records(dataset)

    response = client.get(f"/api/datasets/TextClassification/{dataset}/labeling/rules")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_dataset_update_rule():
    dataset = "test_dataset_with_rules"
    query = "a query"
    log_some_records(dataset)

    response = client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(query=query, label="LALA").dict(),
    )
    assert response.status_code == 200

    client.patch(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{query}",
        json={"label": "NEW Label"},
    )

    response = client.get(f"/api/datasets/TextClassification/{dataset}/labeling/rules")
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0].label == "NEW Label"
    assert rules[0].description is None

    client.patch(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{query}",
        json={"label": "NEW Label", "description": "New description"},
    )

    response = client.get(f"/api/datasets/TextClassification/{dataset}/labeling/rules")
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0].description == "New description"


def test_dataset_with_rules():
    dataset = "test_dataset_with_rules"
    log_some_records(dataset)

    response = client.post(
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

    response = client.get(f"/api/datasets/TextClassification/{dataset}/labeling/rules")
    assert response.status_code == 200
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0] == created_rule


def test_get_dataset_rule():
    dataset = "test_get_dataset_rule"
    log_some_records(dataset)

    rule_query = "a query"
    rule_label = "TEST"
    rule_description = "Description"
    response = client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(
            query=rule_query, label=rule_label, description=rule_description
        ).dict(),
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{rule_query}"
    )
    assert response.status_code == 200
    rule = LabelingRule.parse_obj(response.json())
    assert rule.query == rule_query
    assert rule.label == rule_label
    assert rule.description == rule_description


def test_delete_dataset_rules():
    dataset = "test_delete_dataset_rules"
    log_some_records(dataset)

    response = client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(
            query="a query", label="TEST", description="Description"
        ).dict(),
    )
    assert response.status_code == 200

    response = client.delete(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{'a query'}"
    )
    assert response.status_code == 200

    response = client.get(f"/api/datasets/TextClassification/{dataset}/labeling/rules")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_duplicated_dataset_rules():
    dataset = "test_duplicated_dataset_rules"
    log_some_records(dataset)

    rule = CreateLabelingRule(query="a query", label="TEST")
    response = client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
    )
    assert response.status_code == 200

    response = client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
    )
    assert response.status_code == 409


def test_rules_with_multi_label_dataset():
    dataset = "test_rules_with_multi_label_dataset"
    log_some_records(dataset, multi_label=True)

    with pytest.raises(
        AssertionError,
        match="Labeling rules are not supported for multi-label datasets",
    ):
        client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query="a query", description="Description", label="LALA"
            ).dict(),
        )


def test_rule_metrics_with_missing_label():
    dataset = "test_rule_metrics_with_missing_label"
    log_some_records(dataset, annotation="OK")

    response = client.get(
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


def test_rule_metrics_with_missing_label_for_stored_rule():
    dataset = "test_rule_metrics_with_missing_label_for_stored_rule"
    log_some_records(dataset, annotation="OK")
    for query in ["ejemplo", "bad query"]:
        client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/bad query/metrics"
    )
    assert response.status_code == 200


def test_create_rules_and_then_log():
    dataset = "test_create_rules_and_then_log"
    log_some_records(dataset, annotation="OK")
    for query in ["ejemplo", "bad query"]:
        client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = client.get(f"/api/datasets/TextClassification/{dataset}/labeling/rules")
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 2

    log_some_records(dataset, annotation="OK", delete=False)
    response = client.get(f"/api/datasets/TextClassification/{dataset}/labeling/rules")
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 2


def test_dataset_rules_metrics():
    dataset = "test_dataset_rules_metrics"
    log_some_records(dataset, annotation="OK")

    for query in ["ejemplo", "bad query"]:
        client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/metrics"
    )
    assert response.status_code == 200, response.json()

    metrics = DatasetLabelingRulesMetricsSummary.parse_obj(response.json())
    assert metrics.coverage == 1
    assert metrics.coverage_annotated == 1
    assert metrics.total_records == 1
    assert metrics.annotated_records == 1


def test_dataset_rules_metrics_without_annotation():
    dataset = "test_dataset_rules_metrics_without_annotation"
    log_some_records(dataset)

    for query in ["ejemplo", "bad query"]:
        client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=CreateLabelingRule(
                query=query, label="TEST", description="Description"
            ).dict(),
        )

    response = client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/metrics"
    )
    assert response.status_code == 200, response.json()

    metrics = DatasetLabelingRulesMetricsSummary.parse_obj(response.json())
    assert metrics.coverage == 1
    assert metrics.total_records == 1
    assert metrics.annotated_records == 0
    assert metrics.coverage_annotated is None


def test_rule_metric():
    dataset = "test_rule_metric"
    log_some_records(dataset, annotation="OK")

    response = client.get(
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

    response = client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics?label=OK"
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.correct == 1
    assert metrics.incorrect == 0
    assert metrics.precision == 1

    response = client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics"
    )
    assert response.status_code == 200

    metrics = LabelingRuleMetricsSummary.parse_obj(response.json())
    assert metrics.correct == 0
    assert metrics.incorrect == 0
    assert metrics.precision is None
    assert metrics.coverage_annotated == 1

    response = client.get(
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
