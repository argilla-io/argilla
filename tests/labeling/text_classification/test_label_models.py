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
import importlib
import sys

import numpy as np
import pytest

from rubrix import TextClassificationRecord
from rubrix.labeling.text_classification import Snorkel, WeakLabels
from rubrix.labeling.text_classification.label_models import LabelModel


@pytest.fixture
def weak_labels(monkeypatch):
    def mock_load(*args, **kwargs):
        return [TextClassificationRecord(inputs="test", id=i) for i in range(5)]

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    def mock_apply(self, *args, **kwargs):
        weak_label_matrix = np.array(
            [[0, 1, -1], [2, 0, -1], [-1, -1, -1]],
            dtype=np.short,
        )
        annotation_array = np.array([0, 1, -1], dtype=np.short)
        label2int = {None: -1, "negative": 0, "positive": 1, "neutral": 2}
        return weak_label_matrix, annotation_array, label2int

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    return WeakLabels(rules=[], dataset="mock")


def test_weak_label_property():
    weak_labels = object()
    label_model = LabelModel(weak_labels)

    assert label_model.weak_labels is weak_labels


@pytest.fixture
def uninstall_snorkel(monkeypatch):
    from rubrix.labeling.text_classification import label_models

    saved_module = sys.modules["snorkel"]
    sys.modules["snorkel"] = None
    importlib.reload(label_model)
    yield
    sys.modules["snorkel"] = saved_module
    importlib.reload(label_model)


def test_snorkel_not_installed(uninstall_snorkel):
    with pytest.raises(ImportError) as error:
        Snorkel(None)
        assert "pip install snorkel" in str(error)


def test_snorkel_init(weak_labels):
    from snorkel.labeling.model import LabelModel as SnorkelLabelModel

    label_model = Snorkel(weak_labels)

    assert label_model.weak_labels is weak_labels
    assert isinstance(label_model._model, SnorkelLabelModel)
    assert label_model._model.cardinality == 3


@pytest.mark.parametrize(
    "wrong_mapping",
    [
        {None: -10, "negative": 0, "positive": 1, "neutral": 2},
        {None: -1, "negative": 1, "positive": 3, "neutral": 4},
    ],
)
def test_snorkel_init_wrong_mapping(weak_labels, wrong_mapping):
    weak_labels.change_mapping(wrong_mapping)
    label_model = Snorkel(weak_labels)

    assert label_model.weak_labels.label2int == {
        None: -1,
        "negative": 0,
        "positive": 1,
        "neutral": 2,
    }


@pytest.mark.parametrize(
    "include_annotated_records,no_annotations",
    [(True, False), (False, True)],
)
def test_snorkel_fit(
    monkeypatch, weak_labels, include_annotated_records, no_annotations
):
    def mock_fit(self, L_train, Y_dev, *args, **kwargs):
        if include_annotated_records:
            assert (L_train == weak_labels.matrix()).all()
        else:
            assert (L_train == weak_labels.matrix(has_annotation=False)).all()
        if no_annotations:
            assert Y_dev is None
        else:
            assert (Y_dev == weak_labels.annotation()).all()
        assert kwargs == {"passed_on": None}

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.label_model.SnorkelLabelModel.fit",
        mock_fit,
    )

    if no_annotations:
        weak_labels._annotation_array = np.array([-1, -1, -1], dtype=np.short)
    label_model = Snorkel(weak_labels)
    label_model.fit(include_annotated_records=include_annotated_records, passed_on=None)


@pytest.mark.parametrize("kwargs", [{"L_train": None}, {"Y_dev": None}])
def test_snorkel_fit_automatically_added_kwargs(weak_labels, kwargs):
    label_model = Snorkel(weak_labels)
    with pytest.raises(ValueError) as error:
        label_model.fit(**kwargs)
        assert "provided automatically" in str(error)


@pytest.mark.parametrize(
    "policy,include_annotated_records,include_abstentions,expected",
    [
        ("abstain", True, False, (1, ["positive"], [0.8])),
        ("abstain", True, True, (3, [None, None, "positive"], [None, None, 0.8])),
        ("random", False, True, (1, ["positive"], [0.8])),
        (
            "random",
            True,
            True,
            (
                3,
                ["positive", "negative", "positive"],
                [0.4 + 0.0001, 1.0 / 3 + 0.0001, 0.8],
            ),
        ),
    ],
)
def test_snorkel_predict(
    weak_labels,
    monkeypatch,
    policy,
    include_annotated_records,
    include_abstentions,
    expected,
):
    def mock_predict(self, L, return_probs, tie_break_policy, *args, **kwargs):
        if include_annotated_records:
            assert len(L) == 3
            preds = np.array([-1, -1, 1])
            if policy == "random":
                preds = np.array([1, 0, 1])
            return preds, np.array(
                [
                    [0.4, 0.4, 0.2],
                    [1.0 / 3, 1.0 / 3, 1.0 / 3],
                    [0.1, 0.8, 0.1],
                ]
            )
        else:
            assert len(L) == 1
            return np.array([1]), np.array([[0.1, 0.8, 0.1]])

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.label_model.SnorkelLabelModel.predict",
        mock_predict,
    )

    label_model = Snorkel(weak_labels)

    records = label_model.predict(
        tie_break_policy=policy,
        include_annotated_records=include_annotated_records,
        include_abstentions=include_abstentions,
    )
    assert len(records) == expected[0]
    assert [
        rec.prediction[0][0] if rec.prediction else None for rec in records
    ] == expected[1]
    assert [
        rec.prediction[0][1] if rec.prediction else None for rec in records
    ] == expected[2]


def test_snorkel_score():
    raise NotImplementedError


@pytest.fixture
def weak_labels_from_guide(monkeypatch):
    matrix_and_annotation = np.load("weak-supervision-guide-matrix.npy")
    matrix, annotation = matrix_and_annotation[:, :-1], matrix_and_annotation[:, -1]

    def mock_load(*args, **kwargs):
        return [
            TextClassificationRecord(inputs="mock", id=i) for i in range(len(matrix))
        ]

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    def mock_apply(self, *args, **kwargs):
        return matrix, annotation, {None: -1, "SPAM": 0, "HAM": 1}

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    return WeakLabels(rules=[lambda x: "mock"] * matrix.shape[1], dataset="mock")


def test_snorkel_integration(weak_labels_from_guide):
    matrix_and_annotation = np.load("weak-supervision-guide-matrix.npy")
    matrix, annotation = matrix_and_annotation[:, :-1], matrix_and_annotation[:, -1]

    weak_labels._matrix, weak_labels._annotation_array = matrix, annotation

    label_model = Snorkel(weak_labels_from_guide)
    label_model.fit()
    label_model.score()
    label_model.predict()
