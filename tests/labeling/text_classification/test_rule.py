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
from rubrix.labeling.text_classification.rule import Rule, RuleNotAppliedError
from tests.server.test_helpers import client


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
