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
import numpy as np
import pytest

from rubrix import TextClassificationRecord
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from rubrix.labeling.text_classification.rule import Rule
from rubrix.labeling.text_classification.weak_labels import WeakLabels
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
    "label2int, expected_label2int, expected_matrix",
    [
        (
            None,
            {"None": -1, "negative": 0, "positive": 1},
            np.array([[0, -1, -1], [-1, 1, 1]], dtype=np.short),
        ),
        ({}, None, None),
        (
            {"None": -100, "negative": 50, "positive": 100},
            {"None": -100, "negative": 50, "positive": 100},
            np.array([[50, -100, -100], [-100, 100, 100]], dtype=np.short),
        ),
    ],
)
def test_apply(
    monkeypatch, log_dataset, rules, label2int, expected_label2int, expected_matrix
):
    def mock_apply(self, *args, **kwargs):
        self._matching_ids = [2]

    monkeypatch.setattr(Rule, "apply", mock_apply)

    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "stream", client.stream)

    if label2int == {}:
        with pytest.raises(KeyError):
            WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)
        return

    weak_labels = WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)

    # check that all `Rule.apply`s are called
    assert weak_labels._rules[-1]._matching_ids == [2]

    assert weak_labels.label2int == expected_label2int
    assert (weak_labels.matrix == expected_matrix).all()
