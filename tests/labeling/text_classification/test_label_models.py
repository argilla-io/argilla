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

# we importlib.reload the `label_models` module during the tests, so avoid loading namespaces from this module!
# for example, don't do `from rubrix.labeling.text_classification.label_models import MissingAnnotationError`
# instead do `from rubrix.labeling.text_classification import label_models; label_models.MissingAnnotationError`
from rubrix.labeling.text_classification import (
    FlyingSquid,
    Snorkel,
    WeakLabels,
    label_models,
)


@pytest.fixture
def weak_labels(monkeypatch):
    def mock_load(*args, **kwargs):
        return [TextClassificationRecord(inputs="test", id=i) for i in range(4)]

    monkeypatch.setattr(
        "rubrix.labeling.text_classification.weak_labels.load", mock_load
    )

    def mock_apply(self, *args, **kwargs):
        weak_label_matrix = np.array(
            [[0, 1, -1], [2, 0, -1], [-1, -1, -1], [0, 2, 2]],
            dtype=np.short,
        )
        annotation_array = np.array([0, 1, -1, 2], dtype=np.short)
        label2int = {None: -1, "negative": 0, "positive": 1, "neutral": 2}
        return weak_label_matrix, annotation_array, label2int

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    return WeakLabels(rules=[lambda: None] * 3, dataset="mock")


@pytest.fixture
def weak_labels_from_guide(monkeypatch, resources):
    matrix_and_annotation = np.load(
        str(resources / "weak-supervision-guide-matrix.npy")
    )
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


@pytest.fixture
def uninstall_snorkel(monkeypatch):
    saved_module = sys.modules["snorkel"]
    sys.modules["snorkel"] = None
    importlib.reload(label_models)
    yield
    sys.modules["snorkel"] = saved_module
    importlib.reload(label_models)


@pytest.fixture
def uninstall_flyingsquid(monkeypatch):
    saved_module = sys.modules["flyingsquid"]
    sys.modules["flyingsquid"] = None
    importlib.reload(label_models)
    yield
    sys.modules["flyingsquid"] = saved_module
    importlib.reload(label_models)


class TestLabelModel:
    def test_weak_label_property(self):
        weak_labels = object()
        label_model = label_models.LabelModel(weak_labels)

        assert label_model.weak_labels is weak_labels

    def test_abstract_methods(self):
        label_model = label_models.LabelModel(None)
        with pytest.raises(NotImplementedError):
            label_model.fit()
        with pytest.raises(NotImplementedError):
            label_model.score()
        with pytest.raises(NotImplementedError):
            label_model.predict()


class TestSnorkel:
    def test_not_installed(self, uninstall_snorkel):
        with pytest.raises(ModuleNotFoundError, match="pip install snorkel"):
            Snorkel(None)

    def test_init(self, weak_labels):
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
    def test_init_wrong_mapping(self, weak_labels, wrong_mapping):
        weak_labels.change_mapping(wrong_mapping)
        label_model = Snorkel(weak_labels)

        assert label_model.weak_labels.label2int == {
            None: -1,
            "negative": 0,
            "positive": 1,
            "neutral": 2,
        }

    @pytest.mark.parametrize(
        "include_annotated_records",
        [True, False],
    )
    def test_fit(self, monkeypatch, weak_labels, include_annotated_records):
        def mock_fit(self, L_train, *args, **kwargs):
            if include_annotated_records:
                assert (L_train == weak_labels.matrix()).all()
            else:
                assert (L_train == weak_labels.matrix(has_annotation=False)).all()
            assert kwargs == {"passed_on": None}

        monkeypatch.setattr(
            "rubrix.labeling.text_classification.label_models.SnorkelLabelModel.fit",
            mock_fit,
        )

        label_model = Snorkel(weak_labels)
        label_model.fit(
            include_annotated_records=include_annotated_records, passed_on=None
        )

    def test_fit_automatically_added_kwargs(self, weak_labels):
        label_model = Snorkel(weak_labels)
        with pytest.raises(ValueError, match="provided automatically"):
            label_model.fit(L_train=None)

    @pytest.mark.parametrize(
        "policy,include_annotated_records,include_abstentions,expected",
        [
            ("abstain", True, False, (2, ["positive", "negative"], [0.8, 0.9])),
            (
                "abstain",
                True,
                True,
                (4, [None, None, "positive", "negative"], [None, None, 0.8, 0.9]),
            ),
            ("random", False, True, (1, ["positive"], [0.8])),
            (
                "random",
                True,
                True,
                (
                    4,
                    ["positive", "negative", "positive", "negative"],
                    [0.4 + 0.0001, 1.0 / 3 + 0.0001, 0.8, 0.9],
                ),
            ),
        ],
    )
    def test_predict(
        self,
        weak_labels,
        monkeypatch,
        policy,
        include_annotated_records,
        include_abstentions,
        expected,
    ):
        def mock_predict(self, L, return_probs, tie_break_policy, *args, **kwargs):
            assert tie_break_policy == policy
            assert return_probs is True
            if include_annotated_records:
                assert len(L) == 4
                preds = np.array([-1, -1, 1, 0])
                if policy == "random":
                    preds = np.array([1, 0, 1, 0])
                return preds, np.array(
                    [
                        [0.4, 0.4, 0.2],
                        [1.0 / 3, 1.0 / 3, 1.0 / 3],
                        [0.1, 0.8, 0.1],
                        [0.9, 0.05, 0.05],
                    ]
                )
            else:
                assert len(L) == 1
                return np.array([1]), np.array([[0.1, 0.8, 0.1]])

        monkeypatch.setattr(
            "rubrix.labeling.text_classification.label_models.SnorkelLabelModel.predict",
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

    @pytest.mark.parametrize("policy,expected", [("abstain", 0.5), ("random", 2.0 / 3)])
    def test_score(self, monkeypatch, weak_labels, policy, expected):
        def mock_predict(self, L, return_probs, tie_break_policy):
            assert (L == weak_labels.matrix(has_annotation=True)).all()
            assert return_probs is True
            assert tie_break_policy == policy
            if policy == "abstain":
                predictions = np.array([-1, 1, 0])
            elif policy == "random":
                predictions = np.array([0, 1, 0])
            else:
                raise ValueError("Untested policy!")

            probabilities = None  # accuracy does not need probabs ...

            return predictions, probabilities

        monkeypatch.setattr(
            "rubrix.labeling.text_classification.label_models.SnorkelLabelModel.predict",
            mock_predict,
        )

        label_model = Snorkel(weak_labels)
        assert label_model.score(tie_break_policy=policy)["accuracy"] == pytest.approx(
            expected
        )

    def test_score_without_annotations(self, weak_labels):
        weak_labels._annotation_array = np.array([], dtype=np.short)
        label_model = Snorkel(weak_labels)

        with pytest.raises(
            label_models.MissingAnnotationError, match="need annotated records"
        ):
            label_model.score()

    def test_integration(self, weak_labels_from_guide):
        label_model = Snorkel(weak_labels_from_guide)
        label_model.fit(seed=43)

        metrics = label_model.score()
        assert metrics["accuracy"] == pytest.approx(0.8947368421052632)

        records = label_model.predict()
        assert len(records) == 1177
        assert records[0].prediction == [
            ("SPAM", pytest.approx(0.5633776670811805)),
            ("HAM", pytest.approx(0.4366223329188196)),
        ]


class TestFlyingSquid:
    def test_not_installed(self, uninstall_flyingsquid):
        with pytest.raises(ModuleNotFoundError, match="pip install flyingsquid"):
            FlyingSquid(None)

    def test_init(self, weak_labels):
        label_model = FlyingSquid(weak_labels)
        assert label_model._labels == ["negative", "positive", "neutral"]

        weak_labels._rules = weak_labels.rules[:2]
        with pytest.raises(label_models.TooFewRulesError, match="at least three"):
            FlyingSquid(weak_labels)

    @pytest.mark.parametrize("include_annotated,expected", [(False, 1), (True, 4)])
    def test_fit(self, monkeypatch, weak_labels, include_annotated, expected):
        def mock_fit(*args, **kwargs):
            if not include_annotated:
                assert (kwargs["L_train"] == np.array([0, 0, 0])).all()
            assert len(kwargs["L_train"]) == expected
            assert kwargs["mock"] == "mock"

        monkeypatch.setattr(
            "rubrix.labeling.text_classification.label_models.FlyingSquidLabelModel.fit",
            mock_fit,
        )

        label_model = FlyingSquid(weak_labels)
        label_model.fit(include_annotated_records=include_annotated, mock="mock")

        assert len(label_model._models) == 3

    @pytest.mark.parametrize(
        "policy,include_annotated_records,include_abstentions,verbose,expected",
        [
            (
                "abstain",
                False,
                False,
                True,
                {
                    "verbose": True,
                    "L_matrix_length": 1,
                    "return": np.array([[0.5, 0.5]]),
                    "nr_of_records": 0,
                },
            ),
            (
                "abstain",
                True,
                True,
                False,
                {
                    "verbose": False,
                    "L_matrix_length": 4,
                    "return": np.array([[0.5, 0.5] * 4]),
                    "nr_of_records": 4,
                    "prediction": None,
                },
            ),
            (
                "random",
                False,
                False,
                False,
                {
                    "verbose": False,
                    "L_matrix_length": 1,
                    "return": np.array([[0.5, 0.5]]),
                    "nr_of_records": 1,
                    "prediction": [
                        ("negative", 0.3334333333333333),
                        ("neutral", 0.3332833333333333),
                        ("positive", 0.3332833333333333),
                    ],
                },
            ),
        ],
    )
    def test_predict(
        self,
        weak_labels,
        monkeypatch,
        policy,
        include_annotated_records,
        include_abstentions,
        verbose,
        expected,
    ):
        class MockPredict:
            calls_count = 0

            @classmethod
            def __call__(cls, L_matrix, verbose):
                assert verbose is expected["verbose"]
                assert len(L_matrix) == expected["L_matrix_length"]
                cls.calls_count += 1

                return expected["return"]

        monkeypatch.setattr(
            "rubrix.labeling.text_classification.label_models.FlyingSquidLabelModel.predict_proba",
            MockPredict(),
        )

        label_model = FlyingSquid(weak_labels)
        label_model.fit()

        records = label_model.predict(
            tie_break_policy=policy,
            include_annotated_records=include_annotated_records,
            include_abstentions=include_abstentions,
            verbose=verbose,
        )

        assert MockPredict.calls_count == 3
        assert len(records) == expected["nr_of_records"]
        if records:
            assert records[0].prediction == expected["prediction"]

    def test_predict_binary(self, monkeypatch, weak_labels):
        class MockPredict:
            calls_count = 0

            @classmethod
            def __call__(cls, L_matrix, verbose):
                cls.calls_count += 1
                return np.array([[0.6, 0.4]])

        monkeypatch.setattr(
            "rubrix.labeling.text_classification.label_models.FlyingSquidLabelModel.predict_proba",
            MockPredict(),
        )

        weak_labels._label2int = {None: -1, "negative": 0, "positive": 1}

        label_model = FlyingSquid(weak_labels=weak_labels)
        label_model.fit()

        records = label_model.predict()

        assert MockPredict.calls_count == 1
        assert len(records) == 1
        assert records[0].prediction == [("negative", 0.6), ("positive", 0.4)]

    def test_predict_not_implented_tbp(self, weak_labels):
        label_model = FlyingSquid(weak_labels)

        with pytest.raises(NotImplementedError, match="true-random"):
            label_model.predict(tie_break_policy="true-random")

    def test_integration(self, weak_labels_from_guide):
        label_model = FlyingSquid(weak_labels_from_guide)
        label_model.fit()

        metrics = label_model.score()
        assert metrics["accuracy"] == pytest.approx(1)

        records = label_model.predict()
        assert len(records) == 1177
        assert records[0].prediction == [
            ("SPAM", pytest.approx(0.5633776670811805)),
            ("HAM", pytest.approx(0.4366223329188196)),
        ]
