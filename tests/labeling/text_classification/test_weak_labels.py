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
import pandas as pd
import pytest

from rubrix import TextClassificationRecord
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from rubrix.labeling.text_classification.rule import Rule
from rubrix.labeling.text_classification.weak_labels import (
    DuplicatedRuleNameError,
    MissingLabelError,
    MultiLabelError,
    NoRecordsFoundError,
    NoRulesFoundError,
    WeakLabels,
)


@pytest.fixture
def log_dataset(mocked_client) -> str:
    dataset_name = "test_dataset_for_applier"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    records = [
        CreationTextClassificationRecord.parse_obj(
            {
                "inputs": {"text": text},
                "annotation": {
                    "labels": [{"class": label, "score": 1}],
                    "agent": "test",
                }
                if label is not None
                else None,
                "id": idx,
            }
        )
        for text, label, idx in zip(
            ["negative", "positive", "positive"],
            ["negative", "positive", None],
            [1, 2, 3],
        )
    ]
    mocked_client.post(
        f"/api/datasets/{dataset_name}/TextClassification:bulk",
        json=TextClassificationBulkData(
            records=records,
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture
def rules(monkeypatch) -> List[Callable]:
    def first_rule(record: TextClassificationRecord) -> Optional[str]:
        if "negative" in record.inputs["text"]:
            return "negative"

    def rule2(record: TextClassificationRecord) -> Optional[str]:
        if "positive" in record.inputs["text"]:
            return "positive"

    rule2.__name__ = ""

    def mock_apply(self, *args, **kwargs):
        self._matching_ids = {1: None, 2: None}

    monkeypatch.setattr(Rule, "apply", mock_apply)

    rubrix_rule = Rule(query="mock", label="positive", name="rubrix_rule")

    return [first_rule, rule2, rubrix_rule]


def test_duplicated_rule_name_error():
    rules = [Rule(query="mock", label="mock"), Rule(query="mock", label="not mock")]
    with pytest.raises(DuplicatedRuleNameError, match="'mock': 2"):
        WeakLabels(rules=rules, dataset="mock")


def test_multi_label_error(monkeypatch):
    def mock_load(*args, **kwargs):
        return [TextClassificationRecord(inputs="test", multi_label=True)]

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    with pytest.raises(MultiLabelError):
        WeakLabels(rules=[lambda x: None], dataset="mock")


def test_no_records_found_error(monkeypatch):
    def mock_load(*args, **kwargs):
        return []

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    with pytest.raises(
        NoRecordsFoundError, match="No records found in dataset 'mock'."
    ):
        WeakLabels(rules=[lambda x: None], dataset="mock")
    with pytest.raises(
        NoRecordsFoundError,
        match="No records found in dataset 'mock' with query 'mock'.",
    ):
        WeakLabels(rules=[lambda x: None], dataset="mock", query="mock")
    with pytest.raises(
        NoRecordsFoundError, match="No records found in dataset 'mock' with ids \[-1\]."
    ):
        WeakLabels(rules=[lambda x: None], dataset="mock", ids=[-1])
    with pytest.raises(
        NoRecordsFoundError,
        match="No records found in dataset 'mock' with query 'mock' and with ids \[-1\].",
    ):
        WeakLabels(rules=[lambda x: None], dataset="mock", query="mock", ids=[-1])


@pytest.mark.parametrize(
    "label2int, expected_label2int, expected_matrix, expected_annotation_array",
    [
        (
            None,
            {None: -1, "negative": 0, "positive": 1},
            np.array([[0, -1, 1], [-1, 1, 1], [-1, 1, -1]], dtype=np.short),
            np.array([0, 1, -1], dtype=np.short),
        ),
        (
            {None: -10, "negative": 50, "positive": 10},
            {None: -10, "negative": 50, "positive": 10},
            np.array([[50, -10, 10], [-10, 10, 10], [-10, 10, -10]], dtype=np.short),
            np.array([50, 10, -10], dtype=np.short),
        ),
        ({}, None, None, None),
        ({None: -1}, None, None, None),
        ({None: -1, "negative": 0}, None, None, None),
    ],
)
def test_apply(
    monkeypatch,
    mocked_client,
    log_dataset,
    rules,
    label2int,
    expected_label2int,
    expected_matrix,
    expected_annotation_array,
):
    monkeypatch.setattr(httpx, "get", mocked_client.get)
    monkeypatch.setattr(httpx, "stream", mocked_client.stream)

    if label2int == {}:
        with pytest.raises(MissingLabelError) as error:
            WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)
        assert "required abstention label" in str(error)
        return
    elif label2int == {None: -1}:
        with pytest.raises(MissingLabelError) as error:
            WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)
        assert "annotation label" in str(error)
        return
    elif label2int == {None: -1, "negative": 0}:
        with pytest.raises(MissingLabelError) as error:
            WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)
        assert "weak label" in str(error)
        return

    weak_labels = WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)

    # check that all `Rule.apply`s are called
    assert weak_labels._rules[-1]._matching_ids == {1: None, 2: None}

    assert weak_labels.label2int == expected_label2int
    assert weak_labels.int2label == {v: k for k, v in expected_label2int.items()}
    assert (weak_labels.matrix() == expected_matrix).all()
    assert (weak_labels._annotation_array == expected_annotation_array).all()


def test_rules_matrix_records_annotation(monkeypatch):
    expected_records = [
        TextClassificationRecord(inputs="test without annot"),
        TextClassificationRecord(inputs="test with annot", annotation="positive"),
    ]

    def mock_load(*args, **kwargs):
        return expected_records

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    def mock_apply(self, *args, **kwargs):
        weak_label_matrix = np.array([[0, 1], [-1, 0]], dtype=np.short)
        annotation_array = np.array([-1, 0], dtype=np.short)
        label2int = {None: -1, "negative": 0, "positive": 1}
        return weak_label_matrix, annotation_array, label2int

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    weak_labels = WeakLabels(rules=[lambda x: "mock"] * 2, dataset="mock")

    # records property
    assert len(weak_labels.records()) == 2
    assert weak_labels.records(has_annotation=True) == [expected_records[1]]
    assert weak_labels.records(has_annotation=False) == [expected_records[0]]
    assert isinstance(weak_labels.records()[0], TextClassificationRecord)

    # rules property
    assert len(weak_labels.rules) == 2
    assert weak_labels._rules_name2index == {"rule_0": 0, "rule_1": 1}
    assert weak_labels.rules[0](None) == "mock"

    assert (
        weak_labels.matrix(has_annotation=False) == np.array([[0, 1]], dtype=np.short)
    ).all()
    assert (
        weak_labels.matrix(has_annotation=True) == np.array([[-1, 0]], dtype=np.short)
    ).all()
    assert (weak_labels.annotation() == np.array([[0]], dtype=np.short)).all()
    assert (
        weak_labels.annotation(include_missing=True)
        == np.array([[-1, 0]], dtype=np.short)
    ).all()
    with pytest.warns(
        FutureWarning, match="'exclude_missing_annotations' is deprecated"
    ):
        weak_labels.annotation(exclude_missing_annotations=True)


def test_summary(monkeypatch, rules):
    def mock_load(*args, **kwargs):
        return [TextClassificationRecord(inputs="test")] * 4

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    def mock_apply(self, *args, **kwargs):
        weak_label_matrix = np.array(
            [[0, 1, -1], [-1, 0, -1], [-1, -1, -1], [1, 1, -1]], dtype=np.short
        )
        # weak_label_matrix = np.random.randint(-1, 30, (int(1e5), 50), dtype=np.short)
        annotation_array = np.array([-1, -1, -1, -1], dtype=np.short)
        # annotation_array = np.random.randint(-1, 30, int(1e5), dtype=np.short)
        label2int = {None: -1, "negative": 0, "positive": 1}
        # label2int = {k: v for k, v in zip(["None"]+list(range(30)), list(range(-1, 30)))}
        return weak_label_matrix, annotation_array, label2int

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    weak_labels = WeakLabels(rules=rules, dataset="mock")

    summary = weak_labels.summary()
    expected = pd.DataFrame(
        {
            "label": [
                {"negative", "positive"},
                {"negative", "positive"},
                set(),
                {"negative", "positive"},
            ],
            "coverage": [2.0 / 4, 3.0 / 4, 0, 3.0 / 4],
            "overlaps": [2.0 / 4, 2.0 / 4, 0, 2.0 / 4],
            "conflicts": [1.0 / 4, 1.0 / 4, 0, 1.0 / 4],
        },
        index=["first_rule", "rule_1", "rubrix_rule", "total"],
    )
    pd.testing.assert_frame_equal(summary, expected)

    summary = weak_labels.summary(normalize_by_coverage=True)
    expected = pd.DataFrame(
        {
            "label": [
                {"negative", "positive"},
                {"negative", "positive"},
                set(),
                {"negative", "positive"},
            ],
            "coverage": [2.0 / 4, 3.0 / 4, 0, 3.0 / 4],
            "overlaps": [2.0 / 2, 2.0 / 3, 0, 2.0 / 3],
            "conflicts": [1.0 / 2, 1.0 / 3, 0, 1.0 / 3],
        },
        index=["first_rule", "rule_1", "rubrix_rule", "total"],
    )
    pd.testing.assert_frame_equal(summary, expected)

    summary = weak_labels.summary(annotation=np.array([1, -1, 0, 1]))
    expected = pd.DataFrame(
        {
            "label": [
                {"negative", "positive"},
                {"negative", "positive"},
                set(),
                {"negative", "positive"},
            ],
            "coverage": [2.0 / 4, 3.0 / 4, 0, 3.0 / 4],
            "annotated_coverage": [2.0 / 3, 2.0 / 3, 0, 2.0 / 3],
            "overlaps": [2.0 / 4, 2.0 / 4, 0, 2.0 / 4],
            "conflicts": [1.0 / 4, 1.0 / 4, 0, 1.0 / 4],
            "correct": [1, 2, 0, 3],
            "incorrect": [1, 0, 0, 1],
            "precision": [1.0 / 2, 2 / 2, np.nan, 3.0 / 4],
        },
        index=["first_rule", "rule_1", "rubrix_rule", "total"],
    )
    pd.testing.assert_frame_equal(summary, expected)


def test_show_records(monkeypatch, rules):
    def mock_load(*args, **kwargs):
        return [TextClassificationRecord(inputs="test", id=i) for i in range(5)]

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    def mock_apply(self, *args, **kwargs):
        weak_label_matrix = np.array(
            [[0, 1, -1], [2, 0, -1], [-1, -1, -1], [1, 1, -1], [-1, 0, 2]],
            dtype=np.short,
        )
        annotation_array = np.array([0, 1, -1, 2, 0], dtype=np.short)
        label2int = {None: -1, "negative": 0, "positive": 1, "neutral": 2}
        return weak_label_matrix, annotation_array, label2int

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    weak_labels = WeakLabels(rules=rules, dataset="mock")

    assert weak_labels.show_records().id.tolist() == [0, 1, 2, 3, 4]
    assert weak_labels.show_records(labels=["positive"]).id.tolist() == [0, 3]
    assert weak_labels.show_records(labels=["negative", "neutral"]).id.tolist() == [
        1,
        4,
    ]
    assert weak_labels.show_records(rules=[0]).id.tolist() == [0, 1, 3]
    assert weak_labels.show_records(rules=[0, "rule_1"]).id.tolist() == [0, 1, 3]
    assert weak_labels.show_records(labels=["negative"], rules=[1]).id.tolist() == [
        0,
        1,
        4,
    ]
    assert weak_labels.show_records(labels=["positive"], rules=["rubrix_rule"]).empty


def test_change_mapping(monkeypatch, rules):
    def mock_load(*args, **kwargs):
        return [TextClassificationRecord(inputs="test", id=i) for i in range(5)]

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    def mock_apply(self, *args, **kwargs):
        weak_label_matrix = np.array(
            [[0, 1, -1], [2, 0, -1], [-1, -1, -1], [1, 1, -1], [-1, 0, 2]],
            dtype=np.short,
        )
        annotation_array = np.array([0, 1, -1, 2, 0], dtype=np.short)
        label2int = {None: -1, "negative": 0, "positive": 1, "neutral": 2}
        return weak_label_matrix, annotation_array, label2int

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    weak_labels = WeakLabels(rules=rules, dataset="mock")

    with pytest.raises(MissingLabelError):
        weak_labels.change_mapping({"negative": 2})

    new_mapping = {None: -10, "negative": 2, "positive": 10, "neutral": 1}

    old_wlm = weak_labels.matrix().copy()
    old_mapping = weak_labels.label2int.copy()

    weak_labels.change_mapping(new_mapping)

    assert (
        weak_labels.matrix()
        == np.array(
            [[2, 10, -10], [1, 2, -10], [-10, -10, -10], [10, 10, -10], [-10, 2, 1]],
            dtype=np.short,
        )
    ).all()
    assert (
        weak_labels.annotation(include_missing=True)
        == np.array([2, 10, -10, 1, 2], dtype=np.short)
    ).all()
    assert weak_labels.label2int == new_mapping
    assert weak_labels.int2label == {val: key for key, val in new_mapping.items()}

    weak_labels.change_mapping(old_mapping)

    assert (weak_labels.matrix() == old_wlm).all()


def test_dataset_type_error():
    with pytest.raises(TypeError, match="must be a string, but you provided"):
        WeakLabels([1, 2, 3])


def test_rules_from_dataset(monkeypatch, mocked_client, log_dataset):
    monkeypatch.setattr(httpx, "get", mocked_client.get)
    monkeypatch.setattr(httpx, "stream", mocked_client.stream)

    mock_rules = [Rule(query="mock", label="mock")]
    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load_rules",
        lambda x: mock_rules,
    )

    wl = WeakLabels(log_dataset)
    assert wl.rules is mock_rules


def test_norulesfounderror(monkeypatch):
    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load_rules", lambda x: []
    )

    with pytest.raises(NoRulesFoundError, match="No rules were found"):
        WeakLabels("mock")
