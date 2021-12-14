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

from rubrix import load
from rubrix.client.models import TextClassificationRecord
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from rubrix.labeling.text_classification.rule import (
    Rule,
    RuleMetrics,
    RuleNotAppliedError,
    rule_metrics,
    rules_from_dataset,
)
from tests.server.test_helpers import client, mocking_client


@pytest.fixture(scope="module")
def log_dataset() -> str:
    dataset_name = "test_dataset_for_rule"
    client.delete(f"/api/datasets/{dataset_name}")
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
        for text, label, idx in zip(
            ["negative", "positive"], ["negative", "positive"], [1, 2]
        )
    ]
    client.post(
        f"/api/datasets/{dataset_name}/TextClassification:bulk",
        json=TextClassificationBulkData(
            records=records,
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.mark.parametrize(
    "name,expected", [(None, "query_string"), ("test_name", "test_name")]
)
def test_name(name, expected):
    rule = Rule(query="query_string", label="mock", name=name)
    assert rule.name == expected


def test_apply(monkeypatch, log_dataset):
    rule = Rule(query="inputs.text:(NOT positive)", label="negative")
    with pytest.raises(RuleNotAppliedError):
        rule(TextClassificationRecord(inputs="test"))

    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "stream", client.stream)

    rule.apply(log_dataset)
    assert rule._matching_ids == {1: None}


def test_call(monkeypatch, log_dataset):
    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "stream", client.stream)

    rule = Rule(query="inputs.text:(NOT positive)", label="negative")
    rule.apply(log_dataset)

    records = load(log_dataset, as_pandas=False)
    assert rule(records[0]) == "negative"
    assert rule(records[1]) is None


def test_dataset_rules(monkeypatch, log_dataset):
    mocking_client(monkeypatch, client)

    client.post(
        f"/api/datasets/TextClassification/{log_dataset}/labeling/rules",
        json={"query": "a query", "label": "LALA"},
    )

    rules = rules_from_dataset(log_dataset)
    assert len(rules) == 1
    assert rules[0].query == "a query"
    assert rules[0].label == "LALA"


@pytest.mark.parametrize(
    ["rule", "expected_metrics"],
    [
        (
            Rule(query="neg*", label="LALA"),
            RuleMetrics(
                correct=0,
                incorrect=1,
                coverage=0.5,
                coverage_annotated=0.5,
                precision=0,
            ),
        ),
        (
            Rule(query="neg*", label="negative"),
            RuleMetrics(
                correct=1,
                incorrect=0,
                coverage=0.5,
                coverage_annotated=0.5,
                precision=1,
            ),
        ),
(
            Rule(query="bad", label="negative"),
            RuleMetrics(
                correct=0,
                incorrect=0,
                coverage=0,
                coverage_annotated=0,
                precision=0,
            ),
        ),
    ],
)
def test_dataset_rule_metrics(monkeypatch, log_dataset, rule, expected_metrics):
    mocking_client(monkeypatch, client)

    client.post(
        f"/api/datasets/TextClassification/{log_dataset}/labeling/rules",
        json={"query": rule.query, "label": rule.label},
    )

    metrics = rule_metrics(log_dataset, rule=rule)
    assert metrics == expected_metrics
