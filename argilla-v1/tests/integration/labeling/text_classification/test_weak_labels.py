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
import sys
from typing import Callable, List, Optional, Union

import numpy as np
import pandas as pd
import pytest
from argilla_server.commons.models import TaskType
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from argilla_v1.labeling.text_classification import WeakLabels, WeakMultiLabels
from argilla_v1.labeling.text_classification.rule import Rule
from argilla_v1.labeling.text_classification.weak_labels import (
    DuplicatedRuleNameError,
    MissingLabelError,
    MultiLabelError,
    NoRecordsFoundError,
    NoRulesFoundError,
    WeakLabelsBase,
)
from pandas.testing import assert_frame_equal

from tests.integration.helpers import SecuredClient


@pytest.fixture
def log_dataset(mocked_client: SecuredClient) -> str:
    dataset_name = "test_dataset_for_applier"
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
    def first_rule(record: TextClassificationRecord) -> Optional[Union[str, List[str]]]:
        if "negative" in record.text:
            return "negative"

    def rule2(record: TextClassificationRecord) -> Optional[Union[str, List[str]]]:
        if "positive" in record.text:
            return ["positive"]

    rule2.__name__ = ""

    def mock_apply(self, *args, **kwargs):
        self._matching_ids = {1: None, 2: None}

    monkeypatch.setattr(Rule, "apply", mock_apply)

    argilla_rule = Rule(query="mock", label="positive", name="argilla_rule")

    return [first_rule, rule2, argilla_rule]


@pytest.fixture
def log_multilabel_dataset(mocked_client: SecuredClient) -> str:
    dataset_name = "test_dataset_for_multilabel_applier"
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
                    "labels": [{"class": label, "score": 1} for label in labels],
                    "agent": "test",
                }
                if labels is not None
                else None,
                "multi_label": True,
                "id": idx,
            }
        )
        for text, labels, idx in zip(
            ["negative", "negative and positive", "None"],
            [["negative"], ["negative", "positive"], None],
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
def multilabel_rules(monkeypatch) -> List[Callable]:
    def first_rule(record: TextClassificationRecord) -> Optional[Union[str, List[str]]]:
        if "negative" in record.text:
            return []

    def rule2(record: TextClassificationRecord) -> Optional[Union[str, List[str]]]:
        if "positive" in record.text:
            return ["negative", "positive"]

    rule2.__name__ = ""

    def mock_apply(self, *args, **kwargs):
        self._matching_ids = {1: None, 2: None}

    monkeypatch.setattr(Rule, "apply", mock_apply)

    argilla_rule = Rule(query="mock", label="positive", name="argilla_rule")

    return [first_rule, rule2, argilla_rule]


class TestWeakLabelsBase:
    def test_dataset_type_error(self):
        with pytest.raises(TypeError, match="must be a string, but you provided"):
            WeakLabelsBase([1, 2, 3])

    def test_rules_from_dataset(self, monkeypatch, log_dataset):
        mock_rules = [Rule(query="mock", label="mock")]
        monkeypatch.setattr(
            "argilla_v1.labeling.text_classification.weak_labels.load_rules",
            lambda x: mock_rules,
        )

        wl = WeakLabelsBase(log_dataset)
        assert wl.rules is mock_rules

    def test_norulesfounderror(self, monkeypatch):
        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load_rules", lambda x: [])

        with pytest.raises(NoRulesFoundError, match="No rules were found"):
            WeakLabelsBase("mock")

    def test_duplicated_rule_name_error(self):
        rules = [Rule(query="mock", label="mock"), Rule(query="mock", label="not mock")]
        with pytest.raises(DuplicatedRuleNameError, match="'mock': 2"):
            WeakLabelsBase(rules=rules, dataset="mock")

    def test_no_records_found_error(self, monkeypatch):
        def mock_load(*args, **kwargs):
            return []

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        with pytest.raises(NoRecordsFoundError, match="No records found in dataset 'mock'."):
            WeakLabels(rules=[lambda x: None], dataset="mock")
        with pytest.raises(
            NoRecordsFoundError,
            match="No records found in dataset 'mock' with query 'mock'.",
        ):
            WeakLabels(rules=[lambda x: None], dataset="mock", query="mock")
        with pytest.raises(
            NoRecordsFoundError,
            match=r"No records found in dataset 'mock' with ids \[-1\].",
        ):
            WeakLabels(rules=[lambda x: None], dataset="mock", ids=[-1])
        with pytest.raises(
            NoRecordsFoundError,
            match=r"No records found in dataset 'mock' with query 'mock' and with ids \[-1\].",
        ):
            WeakLabels(rules=[lambda x: None], dataset="mock", query="mock", ids=[-1])

    def test_rules_records_properties(self, monkeypatch):
        expected_records = [
            TextClassificationRecord(text="test without annot"),
            TextClassificationRecord(text="test with annot", annotation="positive"),
        ]

        def mock_load(*args, **kwargs):
            return expected_records

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        weak_labels = WeakLabelsBase(rules=[lambda x: "mock"] * 2, dataset="mock")

        # records property
        assert len(weak_labels.records()) == 2
        assert weak_labels.records(has_annotation=True) == [expected_records[1]]
        assert weak_labels.records(has_annotation=False) == [expected_records[0]]
        assert isinstance(weak_labels.records()[0], TextClassificationRecord)

        # rules property
        assert len(weak_labels.rules) == 2
        assert weak_labels._rules_name2index == {"rule_0": 0, "rule_1": 1}
        assert weak_labels.rules[0](None) == "mock"

    def test_not_implemented_errors(self, monkeypatch):
        def mock_load(*args, **kwargs):
            return ["mock"]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        weak_labels = WeakLabelsBase(rules=["mock"], dataset="mock")

        with pytest.raises(NotImplementedError):
            weak_labels.matrix()
        with pytest.raises(NotImplementedError):
            weak_labels.annotation()
        with pytest.raises(NotImplementedError):
            weak_labels.summary()
        with pytest.raises(NotImplementedError):
            weak_labels.show_records()
        with pytest.raises(NotImplementedError):
            _ = weak_labels.labels
        with pytest.raises(NotImplementedError):
            _ = weak_labels.cardinality
        with pytest.raises(NotImplementedError):
            weak_labels.extend_matrix([0.1])

    def test_faiss_not_installed(self, monkeypatch):
        def mock_load(*args, **kwargs):
            return ["mock"]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)
        monkeypatch.setitem(sys.modules, "faiss", None)
        with pytest.raises(ModuleNotFoundError, match="pip install faiss-cpu"):
            weak_labels = WeakLabelsBase(rules=[lambda x: "mock"] * 2, dataset="mock")
            weak_labels._find_dists_and_nearest(None, None, None, None)


class TestWeakLabels:
    def test_multi_label_error(self, monkeypatch):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test", multi_label=True)]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        with pytest.raises(MultiLabelError):
            WeakLabels(rules=[lambda x: None], dataset="mock")

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
        self,
        monkeypatch,
        log_dataset,
        rules,
        label2int,
        expected_label2int,
        expected_matrix,
        expected_annotation_array,
    ):
        if label2int == {}:
            with pytest.raises(MissingLabelError, match="required abstention label"):
                WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)
            return
        elif label2int == {None: -1}:
            with pytest.raises(MissingLabelError, match="annotation label"):
                WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)
            return
        elif label2int == {None: -1, "negative": 0}:
            with pytest.raises(MissingLabelError, match="weak label"):
                WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)
            return

        weak_labels = WeakLabels(rules=rules, dataset=log_dataset, label2int=label2int)

        # check that all `Rule.apply`s are called
        assert weak_labels._rules[-1]._matching_ids == {1: None, 2: None}

        assert weak_labels.label2int == expected_label2int
        assert weak_labels.int2label == {v: k for k, v in expected_label2int.items()}
        assert (weak_labels.matrix() == expected_matrix).all()
        assert (weak_labels._annotation == expected_annotation_array).all()

    def test_apply_MultiLabelError(self, log_dataset):
        with pytest.raises(MultiLabelError, match="For rules that do not return exactly 1 label"):
            WeakLabels(rules=[lambda x: ["a", "b"]], dataset=log_dataset)

    def test_matrix_annotation_properties(self, monkeypatch):
        expected_records = [
            TextClassificationRecord(text="test without annot"),
            TextClassificationRecord(text="test with annot", annotation="positive"),
        ]

        def mock_load(*args, **kwargs):
            return expected_records

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array([[0, 1], [-1, 0]], dtype=np.short)
            annotation_array = np.array([-1, 0], dtype=np.short)
            label2int = {None: -1, "negative": 0, "positive": 1}
            return weak_label_matrix, annotation_array, label2int

        monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

        weak_labels = WeakLabels(rules=[lambda x: "mock"] * 2, dataset="mock")

        assert (weak_labels.matrix(has_annotation=False) == np.array([[0, 1]], dtype=np.short)).all()
        assert (weak_labels.matrix(has_annotation=True) == np.array([[-1, 0]], dtype=np.short)).all()
        assert (weak_labels.annotation() == np.array([[0]], dtype=np.short)).all()
        assert (weak_labels.annotation(include_missing=True) == np.array([[-1, 0]], dtype=np.short)).all()
        with pytest.warns(FutureWarning, match="'exclude_missing_annotations' is deprecated"):
            weak_labels.annotation(exclude_missing_annotations=True)

    def test_summary(self, monkeypatch, rules):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test")] * 4

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array([[0, 1, -1], [-1, 0, -1], [-1, -1, -1], [1, 1, -1]], dtype=np.short)
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
            index=["first_rule", "rule_1", "argilla_rule", "total"],
        )
        assert_frame_equal(summary, expected)

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
            index=["first_rule", "rule_1", "argilla_rule", "total"],
        )
        assert_frame_equal(summary, expected)

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
            index=["first_rule", "rule_1", "argilla_rule", "total"],
        )
        # The "correct" and "incorrect" columns from `expected_summary` may infer a different
        # dtype than `weak_multi_labels.summary()` returns.
        assert_frame_equal(summary, expected, check_dtype=False)

    def test_show_records(self, monkeypatch, rules):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test", id=i) for i in range(5)]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

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
        assert weak_labels.show_records(labels=["positive"], rules=["argilla_rule"]).empty

    def test_change_mapping(self, monkeypatch, rules):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test", id=i) for i in range(5)]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

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
                [
                    [2, 10, -10],
                    [1, 2, -10],
                    [-10, -10, -10],
                    [10, 10, -10],
                    [-10, 2, 1],
                ],
                dtype=np.short,
            )
        ).all()
        assert (weak_labels.annotation(include_missing=True) == np.array([2, 10, -10, 1, 2], dtype=np.short)).all()
        assert weak_labels.label2int == new_mapping
        assert weak_labels.int2label == {val: key for key, val in new_mapping.items()}

        weak_labels.change_mapping(old_mapping)

        assert (weak_labels.matrix() == old_wlm).all()

    @pytest.fixture
    def weak_labels(self, monkeypatch, rules):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test", id=i) for i in range(3)]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array(
                [[0, -1, -1], [-1, 1, -1], [-1, -1, -1]],
                dtype=np.short,
            )
            annotation_array = np.array([0, 1, -1], dtype=np.short)
            label2int = {None: -1, "negative": 0, "positive": 1}
            return weak_label_matrix, annotation_array, label2int

        monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

        return WeakLabels(rules=rules, dataset="mock")

    def test_extend_matrix(self, weak_labels):
        with pytest.raises(
            ValueError,
            match="Embeddings are not optional the first time a matrix is extended.",
        ):
            weak_labels.extend_matrix([1.0, 0.5, 0.5])

        weak_labels.extend_matrix([1.0, 0.5, 0.5], np.array([[0.1, 0.1], [0.1, 0.11], [0.11, 0.1]]))

        np.testing.assert_equal(weak_labels.matrix(), np.array([[0, -1, -1], [-1, 1, -1], [-1, 1, -1]]))

        weak_labels.extend_matrix([1.0, 1.0, 1.0])

        np.testing.assert_equal(weak_labels.matrix(), np.array([[0, -1, -1], [-1, 1, -1], [-1, -1, -1]]))


class TestWeakMultiLabels:
    def test_apply(
        self,
        log_multilabel_dataset,
        multilabel_rules,
    ):
        weak_labels = WeakMultiLabels(rules=multilabel_rules, dataset=log_multilabel_dataset)

        assert weak_labels.labels == ["negative", "positive"]

        # check that all `Rule.apply`s are called
        assert weak_labels._rules[-1]._matching_ids == {1: None, 2: None}

        assert (
            weak_labels.matrix()
            == np.array(
                [
                    [[0, 0], [-1, -1], [0, 1]],
                    [[0, 0], [1, 1], [0, 1]],
                    [[-1, -1], [-1, -1], [-1, -1]],
                ],
                dtype=np.short,
            )
        ).all()

        assert (weak_labels._annotation == np.array([[1, 0], [1, 1], [-1, -1]], dtype=np.short)).all()

    def test_matrix_annotation(self, monkeypatch):
        expected_records = [
            TextClassificationRecord(text="test without annot", multi_label=True),
            TextClassificationRecord(text="test with annot", annotation="positive", multi_label=True),
        ]

        def mock_load(*args, **kwargs):
            return expected_records

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array([[[1, 0], [0, 1]], [[-1, -1], [1, 0]]], dtype=np.short)
            annotation_array = np.array([[-1, -1], [1, 0]], dtype=np.short)
            labels = ["negative", "positive"]
            return weak_label_matrix, annotation_array, labels

        monkeypatch.setattr(WeakMultiLabels, "_apply_rules", mock_apply)

        weak_labels = WeakMultiLabels(rules=[lambda x: "mock"] * 2, dataset="mock")

        assert (weak_labels.matrix(has_annotation=False) == np.array([[[1, 0], [0, 1]]], dtype=np.short)).all()
        assert (weak_labels.matrix(has_annotation=True) == np.array([[[-1, -1], [1, 0]]], dtype=np.short)).all()
        assert (weak_labels.annotation() == np.array([[1, 0]], dtype=np.short)).all()
        assert (weak_labels.annotation(include_missing=True) == np.array([[[-1, -1], [1, 0]]], dtype=np.short)).all()

    def test_summary(self, monkeypatch, multilabel_rules):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test", multi_label=True)] * 4

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array(
                [
                    [[1, 0], [1, 0], [-1, -1]],
                    [[-1, -1], [1, 0], [-1, -1]],
                    [[-1, -1], [-1, -1], [-1, -1]],
                    [[1, 1], [1, 0], [-1, -1]],
                ],
                dtype=np.short,
            )
            # weak_label_matrix = np.random.randint(-1, 30, (int(1e5), 50), dtype=np.short)
            annotation_array = np.array([[-1, -1], [-1, -1], [-1, -1], [-1, -1]], dtype=np.short)
            # annotation_array = np.random.randint(-1, 30, int(1e5), dtype=np.short)
            labels = ["negative", "positive"]
            # label2int = {k: v for k, v in zip(["None"]+list(range(30)), list(range(-1, 30)))}
            return weak_label_matrix, annotation_array, labels

        monkeypatch.setattr(WeakMultiLabels, "_apply_rules", mock_apply)

        weak_labels = WeakMultiLabels(rules=multilabel_rules, dataset="mock")

        summary = weak_labels.summary()
        expected = pd.DataFrame(
            {
                "label": [
                    {"negative", "positive"},
                    {"negative"},
                    set(),
                    {"negative", "positive"},
                ],
                "coverage": [2.0 / 4, 3.0 / 4, 0, 3.0 / 4],
                "overlaps": [2.0 / 4, 2.0 / 4, 0, 2.0 / 4],
            },
            index=["first_rule", "rule_1", "argilla_rule", "total"],
        )
        assert_frame_equal(summary, expected)

        summary = weak_labels.summary(normalize_by_coverage=True)
        expected = pd.DataFrame(
            {
                "label": [
                    {"negative", "positive"},
                    {"negative"},
                    set(),
                    {"negative", "positive"},
                ],
                "coverage": [2.0 / 4, 3.0 / 4, 0, 3.0 / 4],
                "overlaps": [2.0 / 2, 2.0 / 3, 0, 2.0 / 3],
            },
            index=["first_rule", "rule_1", "argilla_rule", "total"],
        )
        assert_frame_equal(summary, expected)

        summary = weak_labels.summary(annotation=np.array([[0, 1], [-1, -1], [0, 1], [1, 1]]))
        expected = pd.DataFrame(
            {
                "label": [
                    {"negative", "positive"},
                    {"negative"},
                    set(),
                    {"negative", "positive"},
                ],
                "coverage": [2.0 / 4, 3.0 / 4, 0, 3.0 / 4],
                "annotated_coverage": [2.0 / 3, 2.0 / 3, 0, 2.0 / 3],
                "overlaps": [2.0 / 4, 2.0 / 4, 0, 2.0 / 4],
                "correct": [2, 1, 0, 3],
                "incorrect": [1, 1, 0, 2],
                "precision": [2.0 / 3, 1.0 / 2, np.nan, 3.0 / 5],
            },
            index=["first_rule", "rule_1", "argilla_rule", "total"],
        )
        # The "correct" and "incorrect" columns from `expected_summary` may infer a different
        # dtype than `weak_multi_labels.summary()` returns.
        assert_frame_equal(summary, expected, check_dtype=False)

    def test_compute_correct_incorrect(self, monkeypatch):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="mock")]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array([[[1, 0, 1, 0], [0, 1, 0, 1]]], dtype=np.short)
            return weak_label_matrix, None, None

        monkeypatch.setattr(WeakMultiLabels, "_apply_rules", mock_apply)

        weak_labels = WeakMultiLabels(rules=[lambda x: "mock"] * 2, dataset="mock")
        correct, incorrect = weak_labels._compute_correct_incorrect(annotation=np.array([[1, 0, 1, 0]]))

        assert np.allclose(correct, np.array([2, 0, 2]))
        assert np.allclose(incorrect, np.array([0, 2, 2]))

    def test_show_records(self, monkeypatch, multilabel_rules):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test", id=i, multi_label=True) for i in range(5)]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array(
                [
                    [[1, 0], [0, 1], [-1, -1]],
                    [[0, 1], [1, 0], [-1, -1]],
                    [[-1, -1], [-1, -1], [-1, -1]],
                    [[0, 1], [0, 1], [-1, -1]],
                    [[-1, -1], [1, 0], [1, 0]],
                ],
                dtype=np.short,
            )
            labels = ["negative", "positive"]
            return weak_label_matrix, None, labels

        monkeypatch.setattr(WeakMultiLabels, "_apply_rules", mock_apply)

        weak_labels = WeakMultiLabels(rules=multilabel_rules, dataset="mock")

        assert weak_labels.show_records().id.tolist() == [0, 1, 2, 3, 4]
        assert weak_labels.show_records(labels=["positive"]).id.tolist() == [0, 1, 3]
        assert weak_labels.show_records(labels=["negative"]).id.tolist() == [0, 1, 4]
        assert weak_labels.show_records(labels=["negative", "positive"]).id.tolist() == [0, 1]

        assert weak_labels.show_records(rules=[0]).id.tolist() == [0, 1, 3]
        assert weak_labels.show_records(rules=[0, "rule_1"]).id.tolist() == [0, 1, 3]
        assert weak_labels.show_records(labels=["negative"], rules=[1]).id.tolist() == [
            0,
            1,
            4,
        ]
        assert weak_labels.show_records(labels=["positive"], rules=["argilla_rule"]).empty

    @pytest.fixture
    def weak_multi_labels(self, monkeypatch, rules):
        def mock_load(*args, **kwargs):
            return [TextClassificationRecord(text="test", id=i, multi_label=True) for i in range(3)]

        monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

        def mock_apply(self, *args, **kwargs):
            weak_label_matrix = np.array(
                [
                    [[0, 1], [-1, -1], [-1, -1]],
                    [[-1, -1], [1, 1], [-1, -1]],
                    [[-1, -1], [-1, -1], [-1, -1]],
                ],
                dtype=np.short,
            )
            annotation_array = np.array([[0, 0], [1, 1], [-1, -1]], dtype=np.short)
            return weak_label_matrix, annotation_array, ["mock1", "mock2"]

        monkeypatch.setattr(WeakMultiLabels, "_apply_rules", mock_apply)

        return WeakMultiLabels(rules=rules, dataset="mock")

    def test_extend_matrix(self, weak_multi_labels):
        with pytest.raises(
            ValueError,
            match="Embeddings are not optional the first time a matrix is extended.",
        ):
            weak_multi_labels.extend_matrix([1.0, 0.5, 0.5])

        weak_multi_labels.extend_matrix([1.0, 0.5, 0.5], np.array([[0.1, 0.1], [0.1, 0.11], [0.11, 0.1]]))

        np.testing.assert_equal(
            weak_multi_labels.matrix(),
            np.array(
                [
                    [[0, 1], [1, 1], [-1, -1]],
                    [[-1, -1], [1, 1], [-1, -1]],
                    [[-1, -1], [1, 1], [-1, -1]],
                ]
            ),
        )

        expected_summary = pd.DataFrame(
            {
                "label": [{"mock2"}, {"mock2", "mock1"}, set(), {"mock2", "mock1"}],
                "coverage": [1 / 3.0, 1.0, 0.0, 1.0],
                "annotated_coverage": [0.5, 1.0, 0.0, 1.0],
                "overlaps": [1 / 3.0, 1 / 3.0, 0.0, 1 / 3.0],
                "correct": [0, 2, 0, 2],
                "incorrect": [1, 2, 0, 3],
                "precision": [0, 0.5, np.nan, 2 / 5.0],
            },
            index=list(weak_multi_labels._rules_name2index.keys()) + ["total"],
        )
        # The "correct" and "incorrect" columns from `expected_summary` may infer a different
        # dtype than `weak_multi_labels.summary()` returns.
        assert_frame_equal(weak_multi_labels.summary(), expected_summary, check_dtype=False)

        expected_show_records = pd.DataFrame(map(lambda x: x.dict(), weak_multi_labels.records()))
        assert_frame_equal(weak_multi_labels.show_records(rules=["rule_1"]), expected_show_records)

        weak_multi_labels.extend_matrix([1.0, 1.0, 1.0])

        np.testing.assert_equal(
            weak_multi_labels.matrix(),
            np.array(
                [
                    [[0, 1], [-1, -1], [-1, -1]],
                    [[-1, -1], [1, 1], [-1, -1]],
                    [[-1, -1], [-1, -1], [-1, -1]],
                ]
            ),
        )
