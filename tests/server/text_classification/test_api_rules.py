import pytest

from rubrix.server.apis.v0.models.text_classification import (
    CreateLabelingRule,
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
    assert rules[0].labels == ["NEW Label"]
    assert rules[0].description is None

    mocked_client.patch(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{query}",
        json={"labels": ["A", "B"], "description": "New description"},
    )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
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
        CreateLabelingRule(
            query="another query", description="Description", labels=["A", "B", "C"]
        ),
    ],
)
def test_dataset_with_rules(mocked_client, rule):
    dataset = "test_dataset_with_rules"
    log_some_records(mocked_client, dataset)

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
    )
    assert response.status_code == 200

    created_rule = LabelingRule.parse_obj(response.json())
    assert created_rule.query == rule.query
    assert created_rule.label == rule.label
    assert created_rule.labels == rule.labels
    assert created_rule.description == rule.description

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules"
    )
    assert response.status_code == 200
    rules = list(map(LabelingRule.parse_obj, response.json()))
    assert len(rules) == 1
    assert rules[0] == created_rule


@pytest.mark.parametrize(
    "rule",
    [
        CreateLabelingRule(query="a query", description="Description", label="LALA"),
        CreateLabelingRule(
            query="/a qu(e|E)ry/", description="Description", label="LALA"
        ),
        CreateLabelingRule(
            query="another query", description="Description", labels=["A", "B", "C"]
        ),
    ],
)
def test_get_dataset_rule(mocked_client, rule):
    dataset = "test_get_dataset_rule"
    log_some_records(mocked_client, dataset)

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
    )
    assert response.status_code == 200

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{rule.query}"
    )
    assert response.status_code == 200
    found_rule = LabelingRule.parse_obj(response.json())
    assert found_rule.query == rule.query
    assert found_rule.label == rule.label
    assert found_rule.labels == rule.labels
    assert found_rule.description == rule.description


def test_delete_dataset_rules(mocked_client):
    dataset = "test_delete_dataset_rules"
    log_some_records(mocked_client, dataset)

    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=CreateLabelingRule(
            query="/a query/", label="TEST", description="Description"
        ).dict(),
    )
    assert response.status_code == 200

    response = mocked_client.delete(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules//a query/"
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

    rule = CreateLabelingRule(query="a query", labels=["TEST"])
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

    rule = CreateLabelingRule(query="a query", description="Description", label="LALA")
    response = mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules",
        json=rule.dict(),
    )
    assert response.status_code == 200
    found_rule = LabelingRule.parse_obj(response.json())

    assert found_rule.query == rule.query
    assert found_rule.label == rule.label
    assert found_rule.labels == rule.labels
    assert found_rule.description == rule.description


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
def test_rule_metrics_with_missing_label_for_stored_rule(
    mocked_client, rule, expected_metrics
):
    dataset = "test_rule_metrics_with_missing_label_for_stored_rule"
    log_some_records(mocked_client, dataset, annotation="o.k.")
    mocked_client.post(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules", json=rule.dict()
    )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/{rule.query}/metrics"
    )
    assert response.status_code == 200
    assert response.json() == expected_metrics


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
def test_dataset_rules_metrics(mocked_client, rules, expected_metrics, annotation):
    dataset = "test_dataset_rules_metrics"
    log_some_records(mocked_client, dataset, annotation=annotation)

    for rule in rules:
        mocked_client.post(
            f"/api/datasets/TextClassification/{dataset}/labeling/rules",
            json=rule.dict(),
        )

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/metrics"
    )
    assert response.status_code == 200, response.json()
    assert response.json() == expected_metrics


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


def test_rule_metric_with_multiple_labels(mocked_client):
    dataset = "test_rule_metric"
    log_some_records(mocked_client, dataset, annotation="OK")

    response = mocked_client.get(
        f"/api/datasets/TextClassification/{dataset}/labeling/rules/ejemplo/metrics?label=A&label=OK"
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
