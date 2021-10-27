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
from typing import Callable, List, Optional

import httpx
import pytest

from rubrix import TextClassificationRecord
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from rubrix.weaksupervision.text_classification.applier import Applier
from rubrix.weaksupervision.text_classification.rule import Rule
from tests.server.test_helpers import client


@pytest.fixture(scope="module")
def log_dataset() -> str:
    dataset_name = "test_dataset_for_applier"
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


@pytest.fixture(scope="module")
def rules() -> List[Callable]:
    def rule1(record: TextClassificationRecord) -> Optional[str]:
        if "negative" in record.inputs["text"]:
            return "negative"

    def rule2(record: TextClassificationRecord) -> Optional[str]:
        if "positive" in record.inputs["text"]:
            return "positive"

    rule3 = Rule(query="mock", label="positive")

    return [rule1, rule2, rule3]


@pytest.mark.parametrize(
    "label2int, expected",
    [
        (None, ["negative", "positive", "None"]),
        ({"negative": 0, "positive": 1, "None": -1}, [0, 1, -1]),
        ({"negative": 0, "positive": 1}, None),
    ],
)
def test_apply(monkeypatch, log_dataset, rules, label2int, expected):
    def mock_apply(self, *args, **kwargs):
        self._matching_ids = [2]

    monkeypatch.setattr(Rule, "apply", mock_apply)

    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "stream", client.stream)

    applier = Applier(rules=rules)

    if expected is None:
        with pytest.raises(KeyError):
            applier(log_dataset, label2int)
        return

    weak_label_matrix = applier(log_dataset, label2int)

    assert weak_label_matrix.shape == (2, 3)
    assert weak_label_matrix[0, 0] == expected[0]
    assert weak_label_matrix[1, 1] == weak_label_matrix[1, 2] == expected[1]
    assert (
        weak_label_matrix[0, 1]
        == weak_label_matrix[0, 2]
        == weak_label_matrix[1, 0]
        == expected[2]
    )
