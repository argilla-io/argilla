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

import numpy as np
import pytest
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.labeling.text_classification import (
    FlyingSquid,
    Snorkel,
    WeakLabels,
    WeakMultiLabels,
)
from argilla_v1.labeling.text_classification.label_models import (
    LabelModel,
    MajorityVoter,
    MissingAnnotationError,
    NotFittedError,
    TieBreakPolicy,
    TooFewRulesError,
)


@pytest.fixture
def weak_labels(monkeypatch):
    def mock_load(*args, **kwargs):
        return [
            TextClassificationRecord(text="test", annotation="negative"),
            TextClassificationRecord(text="test", annotation="positive"),
            TextClassificationRecord(text="test"),
            TextClassificationRecord(text="test", annotation="neutral"),
        ]

    monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

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
    matrix_and_annotation = np.load(str(resources / "weak-supervision-guide-matrix.npy"))
    matrix, annotation = matrix_and_annotation[:, :-1], matrix_and_annotation[:, -1]

    def mock_load(*args, **kwargs):
        return [TextClassificationRecord(text="mock", id=i) for i in range(len(matrix))]

    monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

    def mock_apply(self, *args, **kwargs):
        return matrix, annotation, {None: -1, "SPAM": 0, "HAM": 1}

    monkeypatch.setattr(WeakLabels, "_apply_rules", mock_apply)

    return WeakLabels(rules=[lambda x: "mock"] * matrix.shape[1], dataset="mock")


@pytest.fixture
def weak_multi_labels(monkeypatch):
    def mock_load(*args, **kwargs):
        return [
            TextClassificationRecord(text="test", multi_label=True, annotation=["scared"]),
            TextClassificationRecord(text="test", multi_label=True, annotation=["sad", "scared"]),
            TextClassificationRecord(text="test", multi_label=True, annotation=[]),
            TextClassificationRecord(text="test", multi_label=True),
        ]

    monkeypatch.setattr("argilla_v1.labeling.text_classification.weak_labels.load", mock_load)

    def mock_apply(self, *args, **kwargs):
        weak_label_matrix = np.array(
            [
                [[0, 0, 1], [-1, -1, -1]],
                [[0, 1, 1], [1, 0, 1]],
                [[-1, -1, -1], [-1, -1, -1]],
                [[0, 0, 0], [0, 0, 0]],
            ],
            dtype=np.byte,
        )
        annotation_array = np.array([[0, 0, 1], [1, 0, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.byte)
        labels = ["sad", "happy", "scared"]
        return weak_label_matrix, annotation_array, labels

    monkeypatch.setattr(WeakMultiLabels, "_apply_rules", mock_apply)

    return WeakMultiLabels(rules=[lambda: None] * 2, dataset="mock")


def test_tie_break_policy_enum():
    with pytest.raises(ValueError, match="mock is not a valid TieBreakPolicy"):
        TieBreakPolicy("mock")


class TestLabelModel:
    def test_weak_label_property(self):
        weak_labels = object()
        label_model = LabelModel(weak_labels)

        assert label_model.weak_labels is weak_labels

    def test_abstract_methods(self):
        label_model = LabelModel(None)
        with pytest.raises(NotImplementedError):
            label_model.fit()
        with pytest.raises(NotImplementedError):
            label_model.score()
        with pytest.raises(NotImplementedError):
            label_model.predict()


class TestMajorityVoter:
    def test_no_need_to_fit_error(self):
        mj = MajorityVoter(None)
        with pytest.raises(NotImplementedError, match="No need to call"):
            mj.fit()

    @pytest.mark.parametrize(
        "wls, include_annotated_records, expected",
        [
            ("weak_labels", True, 4),
            ("weak_labels", False, 1),
            ("weak_multi_labels", True, 4),
            ("weak_multi_labels", False, 1),
        ],
    )
    def test_predict(self, monkeypatch, request, wls, include_annotated_records, expected):
        def compute_probs(self, wl_matrix, **kwargs):
            assert len(wl_matrix) == expected
            compute_probs.called = None

        def make_records(self, probabilities, records, **kwargs):
            assert probabilities is None
            return records

        single_or_multi = "multi" if wls == "weak_multi_labels" else "single"
        monkeypatch.setattr(MajorityVoter, f"_compute_{single_or_multi}_label_probs", compute_probs)
        monkeypatch.setattr(MajorityVoter, f"_make_{single_or_multi}_label_records", make_records)

        weak_labels = request.getfixturevalue(wls)
        mj = MajorityVoter(weak_labels)

        assert len(mj.predict(include_annotated_records=include_annotated_records)) == expected
        assert hasattr(compute_probs, "called")

    def test_compute_single_label_probs(self, weak_labels):
        mj = MajorityVoter(weak_labels)
        probs = mj._compute_single_label_probs(weak_labels.matrix())

        expected = np.array(
            [
                [0.5, 0.5, 0.0],
                [0.5, 0, 0.5],
                [1.0 / 3, 1.0 / 3, 1.0 / 3],
                [1.0 / 3, 0.0, 2.0 / 3],
            ]
        )
        assert np.allclose(probs, expected)

    @pytest.mark.parametrize(
        "include_abstentions,tie_break_policy,expected",
        [
            (True, TieBreakPolicy.ABSTAIN, 4),
            (False, TieBreakPolicy.ABSTAIN, 1),
            (True, TieBreakPolicy.RANDOM, 4),
            (False, TieBreakPolicy.RANDOM, 4),
        ],
    )
    def test_make_single_label_records(self, weak_labels, include_abstentions, tie_break_policy, expected):
        mj = MajorityVoter(weak_labels)
        probs = mj._compute_single_label_probs(weak_labels.matrix())

        records = mj._make_single_label_records(
            probs,
            weak_labels.records(),
            include_abstentions,
            prediction_agent="mock",
            tie_break_policy=tie_break_policy,
        )

        assert records[-1].prediction_agent == "mock"
        assert records[-1].prediction == [
            ("neutral", 2.0 / 3),
            ("negative", 1.0 / 3),
            ("positive", 0.0),
        ]
        assert len(records) == expected
        if include_abstentions and tie_break_policy is TieBreakPolicy.ABSTAIN:
            assert all(rec.prediction is None for rec in records[:3])
        if tie_break_policy is TieBreakPolicy.RANDOM:
            assert records[2].prediction == [
                ("negative", 1.0 / 3 + 0.0001),
                ("neutral", 1.0 / 3 - 0.00005),
                ("positive", 1.0 / 3 - 0.00005),
            ]

    def test_make_single_label_records_with_not_implemented_tbp(self, weak_labels):
        mj = MajorityVoter(weak_labels)
        probs = mj._compute_single_label_probs(weak_labels.matrix())

        with pytest.raises(
            NotImplementedError,
            match="tie break policy 'true-random' is not implemented",
        ):
            mj._make_single_label_records(
                probs,
                weak_labels.records(),
                True,
                prediction_agent="mock",
                tie_break_policy=TieBreakPolicy.TRUE_RANDOM,
            )

    def test_compute_multi_label_probs(self, weak_multi_labels):
        mj = MajorityVoter(weak_multi_labels)
        probabilities = mj._compute_multi_label_probs(weak_multi_labels.matrix())

        expected = np.array(
            [[0, 0, 1], [1, 1, 1], [np.nan, np.nan, np.nan], [0, 0, 0]],
            dtype=np.float16,
        )
        assert np.allclose(probabilities, expected, equal_nan=True)

    @pytest.mark.parametrize(
        "include_abstentions,expected",
        [
            (True, 4),
            (False, 3),
        ],
    )
    def test_make_multi_label_records(self, weak_multi_labels, include_abstentions, expected):
        mj = MajorityVoter(weak_multi_labels)
        probs = mj._compute_multi_label_probs(weak_multi_labels.matrix())

        records = mj._make_multi_label_records(
            probs,
            weak_multi_labels.records(),
            include_abstentions,
            prediction_agent="mock",
        )

        assert records[0].prediction_agent == "mock"
        assert records[0].prediction == [
            ("scared", 1.0),
            ("happy", 0.0),
            ("sad", 0.0),
        ]
        assert len(records) == expected
        if include_abstentions:
            assert records[2].prediction is None

    def test_score_sklearn_not_installed(self, monkeypatch, weak_labels):
        monkeypatch.setattr(sys, "meta_path", [], raising=False)

        mj = MajorityVoter(weak_labels)
        with pytest.raises(ModuleNotFoundError, match="pip install scikit-learn"):
            mj.score()

    @pytest.mark.parametrize(
        "wls, output_str",
        [
            ("weak_labels", True),
            ("weak_multi_labels", False),
        ],
    )
    def test_score(self, monkeypatch, request, wls, output_str):
        def compute_probs(self, wl_matrix, **kwargs):
            compute_probs.called = None

        def score(self, probabilities, tie_break_policy=None):
            assert probabilities is None
            if wls == "weak_labels":
                assert tie_break_policy == TieBreakPolicy.ABSTAIN
                return np.array([1, 0]), np.array([1, 1])

            assert tie_break_policy is None
            return np.array([[1, 1, 1], [0, 0, 0]]), np.array([[1, 1, 1], [1, 0, 0]])

        single_or_multi = "multi" if wls == "weak_multi_labels" else "single"
        monkeypatch.setattr(MajorityVoter, f"_compute_{single_or_multi}_label_probs", compute_probs)
        monkeypatch.setattr(MajorityVoter, f"_score_{single_or_multi}_label", score)

        weak_labels = request.getfixturevalue(wls)
        score = MajorityVoter(weak_labels).score(output_str=output_str)
        if output_str:
            assert isinstance(score, str)
        else:
            assert isinstance(score, dict)
            assert "sad" in score and "happy" in score
        assert hasattr(compute_probs, "called")

    @pytest.mark.parametrize(
        "tie_break_policy, expected",
        [
            (TieBreakPolicy.ABSTAIN, (np.array([2]), np.array([2]))),
            (TieBreakPolicy.RANDOM, (np.array([0, 1, 2]), np.array([0, 2, 2]))),
            (TieBreakPolicy.TRUE_RANDOM, None),
        ],
    )
    def test_score_single_label(self, weak_labels, tie_break_policy, expected):
        mj = MajorityVoter(weak_labels)

        probabilities = np.array([[0.5, 0.5, 0.0], [0.5, 0.0, 0.5], [1.0 / 3, 0.0, 2.0 / 3]])

        if tie_break_policy is TieBreakPolicy.TRUE_RANDOM:
            with pytest.raises(NotImplementedError, match="not implemented for MajorityVoter"):
                mj._score_single_label(probabilities, tie_break_policy)
            return

        annotation, prediction = mj._score_single_label(probabilities=probabilities, tie_break_policy=tie_break_policy)
        assert np.allclose(annotation, expected[0])
        assert np.allclose(prediction, expected[1])

    def test_score_single_label_no_ties(self, weak_labels):
        mj = MajorityVoter(weak_labels)

        probabilities = np.array([[0.5, 0.3, 0.0], [0.5, 0.0, 0.0], [1.0 / 3, 0.0, 2.0 / 3]])

        _, prediction = mj._score_single_label(probabilities=probabilities, tie_break_policy=TieBreakPolicy.ABSTAIN)
        _, prediction2 = mj._score_single_label(probabilities=probabilities, tie_break_policy=TieBreakPolicy.RANDOM)

        assert np.allclose(prediction, prediction2)

    def test_score_multi_label(self, weak_multi_labels):
        mj = MajorityVoter(weak_multi_labels)

        probabilities = np.array([[0.0, 0.0, 1.0], [1.0, 1.0, 1.0], [np.nan, np.nan, np.nan]])

        annotation, prediction = mj._score_multi_label(probabilities=probabilities)

        assert np.allclose(annotation, np.array([[0, 0, 1], [1, 0, 1]]))
        assert np.allclose(prediction, np.array([[0, 0, 1], [1, 1, 1]]))


class TestSnorkel:
    def test_not_installed(self, monkeypatch):
        monkeypatch.setattr(sys, "meta_path", [], raising=False)
        with pytest.raises(ModuleNotFoundError, match="pip install snorkel"):
            Snorkel(None)

    def test_init(self, weak_labels):
        from snorkel.labeling.model import LabelModel as SnorkelLabelModel

        label_model = Snorkel(weak_labels)

        assert label_model.weak_labels is weak_labels
        assert isinstance(label_model._model, SnorkelLabelModel)
        assert label_model._model.cardinality == 3

    @pytest.mark.parametrize(
        "wrong_mapping,expected",
        [
            (
                {None: -10, "negative": 0, "positive": 1, "neutral": 2},
                {-10: -1, 0: 0, 1: 1, 2: 2},
            ),
            (
                {None: -1, "negative": 1, "positive": 3, "neutral": 4},
                {-1: -1, 1: 0, 3: 1, 4: 2},
            ),
        ],
    )
    def test_init_wrong_mapping(self, weak_labels, wrong_mapping, expected):
        weak_labels.change_mapping(wrong_mapping)
        label_model = Snorkel(weak_labels)

        assert label_model._weaklabelsInt2snorkelInt == expected
        assert label_model._snorkelInt2weaklabelsInt == {k: v for v, k in expected.items()}

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
            "snorkel.labeling.model.LabelModel.fit",
            mock_fit,
        )

        label_model = Snorkel(weak_labels)
        label_model.fit(include_annotated_records=include_annotated_records, passed_on=None)

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
            "snorkel.labeling.model.LabelModel.predict",
            mock_predict,
        )

        label_model = Snorkel(weak_labels)

        records = label_model.predict(
            tie_break_policy=policy,
            include_annotated_records=include_annotated_records,
            include_abstentions=include_abstentions,
            prediction_agent="mock_agent",
        )
        assert len(records) == expected[0]
        assert [rec.prediction[0][0] if rec.prediction else None for rec in records] == expected[1]
        assert [rec.prediction[0][1] if rec.prediction else None for rec in records] == expected[2]
        assert records[0].prediction_agent == "mock_agent"

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
            "snorkel.labeling.model.LabelModel.predict",
            mock_predict,
        )

        label_model = Snorkel(weak_labels)
        metrics = label_model.score(tie_break_policy=policy)

        assert metrics["accuracy"] == pytest.approx(expected)
        assert list(metrics.keys())[:3] == ["negative", "positive", "neutral"]

    def test_score_without_annotations(self, weak_labels):
        weak_labels._annotation = np.array([], dtype=np.short)
        label_model = Snorkel(weak_labels)

        with pytest.raises(MissingAnnotationError, match="need annotated records"):
            label_model.score()

    @pytest.mark.parametrize(
        "change_mapping",
        [False, True],
    )
    def test_integration(self, weak_labels_from_guide, change_mapping):
        if change_mapping:
            weak_labels_from_guide.change_mapping({None: -10, "HAM": 2, "SPAM": 5})
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
    def test_not_installed(self, monkeypatch):
        monkeypatch.setattr(sys, "meta_path", [], raising=False)
        with pytest.raises(ModuleNotFoundError, match="pip install flyingsquid"):
            FlyingSquid(None)

    def test_init(self, weak_labels):
        FlyingSquid(weak_labels)

        with pytest.raises(ValueError, match="must not contain 'm'"):
            FlyingSquid(weak_labels, m="mock")

        weak_labels._rules = weak_labels.rules[:2]
        with pytest.raises(TooFewRulesError, match="at least three"):
            FlyingSquid(weak_labels)

    @pytest.mark.parametrize("include_annotated,expected", [(False, 1), (True, 4)])
    def test_fit(self, monkeypatch, weak_labels, include_annotated, expected):
        def mock_fit(*args, **kwargs):
            if not include_annotated:
                assert (kwargs["L_train"] == np.array([0, 0, 0])).all()
            assert len(kwargs["L_train"]) == expected

        monkeypatch.setattr(
            "flyingsquid.label_model.LabelModel.fit",
            mock_fit,
        )

        label_model = FlyingSquid(weak_labels)
        label_model.fit(include_annotated_records=include_annotated)

        assert len(label_model._models) == 3

    def test_fit_init_kwargs(self, monkeypatch, weak_labels):
        class MockLabelModel:
            def __init__(self, m, mock):
                assert m == len(weak_labels.rules)
                assert mock == "mock"

            def fit(self, L_train, mock):
                assert mock == "mock_fit_kwargs"

        monkeypatch.setattr(
            "flyingsquid.label_model.LabelModel",
            MockLabelModel,
        )

        label_model = FlyingSquid(weak_labels, mock="mock")
        label_model.fit(mock="mock_fit_kwargs")

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
            "flyingsquid.label_model.LabelModel.predict_proba",
            MockPredict(),
        )

        label_model = FlyingSquid(weak_labels)
        label_model.fit()

        records = label_model.predict(
            tie_break_policy=policy,
            include_annotated_records=include_annotated_records,
            include_abstentions=include_abstentions,
            verbose=verbose,
            prediction_agent="mock_agent",
        )

        assert MockPredict.calls_count == 3
        assert len(records) == expected["nr_of_records"]
        if records:
            assert records[0].prediction == expected["prediction"]
            assert records[0].prediction_agent == "mock_agent"

    def test_predict_binary(self, monkeypatch, weak_labels):
        class MockPredict:
            calls_count = 0

            @classmethod
            def __call__(cls, L_matrix, verbose):
                cls.calls_count += 1
                return np.array([[0.6, 0.4]])

        monkeypatch.setattr(
            "flyingsquid.label_model.LabelModel.predict_proba",
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
        label_model.fit()

        with pytest.raises(NotImplementedError, match="true-random"):
            label_model.predict(tie_break_policy="true-random")

    def test_predict_not_fitted_error(self, weak_labels):
        label_model = FlyingSquid(weak_labels)
        with pytest.raises(NotFittedError, match="not fitted yet"):
            label_model.predict()

    def test_score_not_fitted_error(self, weak_labels):
        label_model = FlyingSquid(weak_labels)
        with pytest.raises(NotFittedError, match="not fitted yet"):
            label_model.score()

    def test_score_sklearn_not_installed(self, monkeypatch: pytest.MonkeyPatch, weak_labels):
        label_model = FlyingSquid(weak_labels)

        monkeypatch.setattr(sys, "meta_path", [], raising=False)
        with pytest.raises(ModuleNotFoundError, match="pip install scikit-learn"):
            label_model.score()

    def test_score(self, monkeypatch, weak_labels):
        def mock_predict(weak_label_matrix, verbose):
            assert verbose is False
            assert len(weak_label_matrix) == 3
            return np.array([[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]])

        label_model = FlyingSquid(weak_labels)
        # We have to monkeypatch the instance rather than the class due to decorators
        # on the class
        monkeypatch.setattr(label_model, "_predict", mock_predict)
        metrics = label_model.score()

        assert "accuracy" in metrics
        assert metrics["accuracy"] == pytest.approx(1.0)
        assert list(metrics.keys())[:3] == ["negative", "positive", "neutral"]

        assert isinstance(label_model.score(output_str=True), str)

    @pytest.mark.parametrize("tbp,vrb,expected", [("abstain", False, 1.0), ("random", True, 2 / 3.0)])
    def test_score_tbp(self, monkeypatch, weak_labels, tbp, vrb, expected):
        def mock_predict(weak_label_matrix, verbose):
            assert verbose is vrb
            assert len(weak_label_matrix) == 3
            return np.array([[0.8, 0.1, 0.1], [0.4, 0.4, 0.2], [1 / 3.0, 1 / 3.0, 1 / 3.0]])

        label_model = FlyingSquid(weak_labels)

        monkeypatch.setattr(label_model, "_predict", mock_predict)

        metrics = label_model.score(tie_break_policy=tbp, verbose=vrb)

        assert metrics["accuracy"] == pytest.approx(expected)
        if tbp == "abstain":
            assert list(metrics.keys())[:1] == ["negative"]
        elif tbp == "random":
            assert list(metrics.keys())[:3] == ["negative", "positive", "neutral"]

    def test_score_not_implemented_tbp(self, weak_labels):
        label_model = FlyingSquid(weak_labels)
        label_model.fit()

        with pytest.raises(NotImplementedError, match="true-random"):
            label_model.score(tie_break_policy="true-random")

    def test_integration(self, weak_labels_from_guide):
        label_model = FlyingSquid(weak_labels_from_guide)
        label_model.fit()

        metrics = label_model.score()
        assert metrics["accuracy"] == pytest.approx(0.9282296650717703)

        records = label_model.predict()
        assert len(records) == 1177

        prediction = records[0].prediction
        spam_prediction_probability = prediction[0][1]
        ham_prediction_probability = prediction[1][1]
        assert spam_prediction_probability == pytest.approx(0.8236983486087645)
        assert ham_prediction_probability == pytest.approx(0.17630165139123552)
