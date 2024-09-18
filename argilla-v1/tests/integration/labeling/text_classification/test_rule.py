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
import httpx
import pytest
from argilla_server.errors import EntityNotFoundError
from argilla_v1 import User
from argilla_v1.client.api import copy, load
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.client.sdk.datasets.models import TaskType
from argilla_v1.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from argilla_v1.labeling.text_classification import (
    Rule,
    add_rules,
    delete_rules,
    load_rules,
    update_rules,
)
from argilla_v1.labeling.text_classification.rule import RuleNotAppliedError

from tests.integration.helpers import SecuredClient
from tests.integration.utils import delete_ignoring_errors


@pytest.fixture
def log_dataset_without_annotations(mocked_client: SecuredClient) -> str:
    dataset_name = "test_dataset_for_rule"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    assert (
        mocked_client.post(
            "/api/datasets", json={"name": dataset_name, "task": TaskType.text_classification.value}
        ).status_code
        == 200
    )
    records = [
        CreationTextClassificationRecord.parse_obj(
            {
                "inputs": {"text": text},
                "id": idx,
            }
        )
        for text, idx in zip(["negative", "positive"], [1, 2])
    ]
    mocked_client.post(
        f"/api/datasets/{dataset_name}/TextClassification:bulk",
        json=TextClassificationBulkData(
            records=records,
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture
def log_dataset(mocked_client) -> str:
    dataset_name = "test_dataset_for_rule"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    assert (
        mocked_client.post(
            "/api/datasets", json={"name": dataset_name, "task": TaskType.text_classification.value}
        ).status_code
        == 200
    )
    records = [
        CreationTextClassificationRecord.parse_obj(
            {
                "inputs": {"text": text},
                "annotation": {
                    "labels": [{"class": label, "score": 1}],
                    "agent": "test",
                },
                "id": idx,
            }
        )
        for text, label, idx in zip(["negative", "positive"], ["negative", "positive"], [1, 2])
    ]
    mocked_client.post(
        f"/api/datasets/{dataset_name}/TextClassification:bulk",
        json=TextClassificationBulkData(
            records=records,
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.mark.parametrize("name,expected", [(None, "query_string"), ("test_name", "test_name")])
def test_name(name, expected):
    rule = Rule(query="query_string", label="mock", name=name)
    assert rule.name == expected


def test_atomic_crud_operations(monkeypatch, mocked_client, log_dataset):
    rule = Rule(query="inputs.text:(NOT positive)", label="negative")
    with pytest.raises(RuleNotAppliedError):
        rule(TextClassificationRecord(text="test"))

    monkeypatch.setattr(httpx, "get", mocked_client.get)
    monkeypatch.setattr(httpx, "patch", mocked_client.patch)
    monkeypatch.setattr(httpx, "delete", mocked_client.delete)
    monkeypatch.setattr(httpx, "post", mocked_client.post)
    monkeypatch.setattr(httpx, "stream", mocked_client.stream)

    rule.add_to_dataset(log_dataset)

    rules = load_rules(log_dataset)
    assert len(rules) == 1
    assert rules[0].query == "inputs.text:(NOT positive)"
    assert rules[0].label == "negative"

    rule.remove_from_dataset(log_dataset)

    rules = load_rules(log_dataset)
    assert len(rules) == 0

    rule = Rule(query="inputs.text:(NOT positive)", label="negative")
    rule.add_to_dataset(log_dataset)
    rule.label = "positive"
    rule.update_at_dataset(log_dataset)

    rules = load_rules(log_dataset)
    assert len(rules) == 1
    assert rules[0].query == "inputs.text:(NOT positive)"
    assert rules[0].label == "positive"


def test_apply(monkeypatch, mocked_client, log_dataset):
    rule = Rule(query="inputs.text:(NOT positive)", label="negative")
    with pytest.raises(RuleNotAppliedError):
        rule(TextClassificationRecord(text="test"))

    monkeypatch.setattr(httpx, "get", mocked_client.get)
    monkeypatch.setattr(httpx, "stream", mocked_client.stream)

    rule.apply(log_dataset)
    assert rule._matching_ids == {1: None}


def test_call(monkeypatch, mocked_client, log_dataset):
    monkeypatch.setattr(httpx, "get", mocked_client.get)
    monkeypatch.setattr(httpx, "stream", mocked_client.stream)

    rule = Rule(query="inputs.text:(NOT positive)", label="negative")
    rule.apply(log_dataset)

    records = load(log_dataset)
    assert rule(records[0]) == "negative"
    assert rule(records[1]) is None


def test_add_duplicated_rule(
    mocked_client,
    log_dataset,
):
    rules = [
        Rule(query="lab", label="DD"),
        Rule(query="lab", label="EF"),
    ]
    add_rules(log_dataset, rules)
    new_rules = load_rules(log_dataset)
    assert len(new_rules) == 1, new_rules
    assert new_rules[0].label == "DD" and new_rules[0].query == "lab"


def test_create_rules_with_update(
    mocked_client,
    log_dataset,
):
    rules = [Rule(query="lab", label="DD"), Rule(query="ob", label="EF")]
    update_rules(log_dataset, rules)

    new_rules = load_rules(log_dataset)
    assert [{"query": r.query, "label": r.label} for r in rules] == [
        {"query": r.query, "label": r.label} for r in new_rules
    ]


def test_load_rules(mocked_client, log_dataset):
    mocked_client.post(
        f"/api/datasets/TextClassification/{log_dataset}/labeling/rules",
        json={"query": "a query", "label": "LALA"},
    )

    rules = load_rules(log_dataset)
    assert len(rules) == 1
    assert rules[0].query == "a query"
    assert rules[0].label == "LALA"


def test_add_rules(mocked_client, log_dataset):
    expected_rules = [
        Rule(query="a query", label="La La"),
        Rule(query="another query", label="La La"),
        Rule(query="the other query", label="La La La"),
    ]

    add_rules(log_dataset, expected_rules)

    actual_rules = load_rules(log_dataset)

    assert len(actual_rules) == 3
    for actual_rule, expected_rule in zip(actual_rules, expected_rules):
        assert actual_rule.query == expected_rule.query
        assert actual_rule.label == expected_rule.label


def test_delete_rules(mocked_client, log_dataset):
    rules = [
        Rule(query="a query", label="La La"),
        Rule(query="another query", label="La La"),
        Rule(query="the other query", label="La La La"),
    ]

    add_rules(log_dataset, rules)

    delete_rules(
        log_dataset,
        [
            Rule(query="a query", label="La La"),
        ],
    )

    actual_rules = load_rules(log_dataset)

    assert len(actual_rules) == 2

    for actual_rule, expected_rule in zip(actual_rules, rules[1:]):
        assert actual_rule.label == expected_rule.label
        assert actual_rule.query == expected_rule.query


def test_update_rules(mocked_client, log_dataset):
    rules = [
        Rule(query="a query", label="La La"),
        Rule(query="another query", label="La La"),
        Rule(query="the other query", label="La La La"),
    ]

    add_rules(log_dataset, rules)
    rules_to_update = [
        Rule(query="a query", label="La La La"),
    ]
    update_rules(log_dataset, rules=rules_to_update)

    actual_rules = load_rules(log_dataset)

    assert len(rules) == 3

    assert actual_rules[0].query == "a query"
    assert actual_rules[0].label == "La La La"

    for actual_rule, expected_rule in zip(actual_rules[1:], rules[1:]):
        assert actual_rule.label == expected_rule.label
        assert actual_rule.query == expected_rule.query


def test_copy_dataset_with_rules(mocked_client: SecuredClient, argilla_user: User):
    dataset_name = "test_copy_dataset_with_rules"

    mocked_client.delete(f"/api/datasets/{dataset_name}")

    mocked_client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": TaskType.text_classification.value, "workspace": argilla_user.username},
    )

    mocked_client.post(
        f"/api/datasets/TextClassification/{log_dataset}/labeling/rules",
        json={"query": "a query", "label": "LALA"},
    )

    copied_dataset = f"{dataset_name}_copy"
    delete_ignoring_errors(copied_dataset)
    copy(dataset_name, name_of_copy=copied_dataset)

    assert [{"q": r.query, "l": r.label} for r in load_rules(copied_dataset)] == [
        {"q": r.query, "l": r.label} for r in load_rules(dataset_name)
    ]


@pytest.mark.parametrize(
    ["rule", "expected_metrics"],
    [
        (
            Rule(query="neg*", label="LALA"),
            dict(
                coverage=0.5,
                annotated_coverage=0.5,
                correct=0,
                incorrect=1,
                precision=0.0,
            ),
        ),
        (
            Rule(query="neg*", label="negative"),
            dict(
                coverage=0.5,
                annotated_coverage=0.5,
                correct=1,
                incorrect=0,
                precision=1.0,
            ),
        ),
        (
            Rule(query="bad", label="negative"),
            dict(
                coverage=0.0,
                annotated_coverage=0.0,
                correct=0,
                incorrect=0,
                precision=None,
            ),
        ),
    ],
)
def test_rule_metrics(mocked_client, log_dataset, rule, expected_metrics):
    delete_rule_silently(mocked_client, log_dataset, rule)

    mocked_client.post(
        f"/api/datasets/TextClassification/{log_dataset}/labeling/rules",
        json={"query": rule.query, "label": rule.label},
    )

    metrics = rule.metrics(log_dataset)
    assert metrics == expected_metrics


@pytest.mark.parametrize(
    ["rule", "expected_metrics"],
    [
        (
            Rule(query="neg*", label="LALA"),
            dict(
                coverage=0.5,
                annotated_coverage=None,
                correct=None,
                incorrect=None,
                precision=None,
            ),
        ),
        (
            Rule(query="neg*", label="negative"),
            dict(
                coverage=0.5,
                annotated_coverage=None,
                correct=None,
                incorrect=None,
                precision=None,
            ),
        ),
        (
            Rule(query="bad", label="negative"),
            dict(
                coverage=0.0,
                annotated_coverage=None,
                correct=None,
                incorrect=None,
                precision=None,
            ),
        ),
    ],
)
def test_rule_metrics_without_annotated(mocked_client, log_dataset_without_annotations, rule, expected_metrics):
    delete_rule_silently(mocked_client, log_dataset_without_annotations, rule)

    mocked_client.post(
        f"/api/datasets/TextClassification/{log_dataset_without_annotations}/labeling/rules",
        json={"query": rule.query, "label": rule.label},
    )

    metrics = rule.metrics(log_dataset_without_annotations)
    assert expected_metrics == metrics


def delete_rule_silently(client, dataset: str, rule: Rule):
    try:
        client.delete(f"/api/datasets/TextClassification/{dataset}/labeling/rules/{rule.query}")
    except EntityNotFoundError:
        pass
