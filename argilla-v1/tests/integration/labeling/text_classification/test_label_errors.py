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

import cleanlab
import pytest
from argilla_v1 import User
from argilla_v1.client.api import delete, load, log
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.client.singleton import init
from argilla_v1.labeling.text_classification import find_label_errors
from argilla_v1.labeling.text_classification.label_errors import (
    MissingPredictionError,
    NoRecordsError,
    SortBy,
    _construct_s_and_psx,
)
from pkg_resources import parse_version


@pytest.fixture(params=[False, True], ids=["single_label", "multi_label"], scope="module")
def records(request):
    if request.param:
        return [
            TextClassificationRecord(text="test", annotation=anot, prediction=pred, multi_label=True, id=i)
            for i, anot, pred in zip(
                range(2 * 6),
                [["bad"], ["bad", "good"]] * 6,
                [[("bad", 0.1), ("good", 0.9)], [("good", 0.9), ("bad", 0.01)]] * 6,
            )
        ]

    return [
        TextClassificationRecord(text="test", annotation=anot, prediction=pred, id=i)
        for i, anot, pred in zip(
            range(2 * 6),
            ["good", "bad"] * 6,
            [[("bad", 0.9), ("good", 0.1)], [("good", 0.8), ("bad", 0.2)]] * 6,
        )
    ]


def test_sort_by_enum():
    with pytest.raises(ValueError, match="mock is not a valid SortBy"):
        SortBy("mock")


def test_not_installed(monkeypatch):
    monkeypatch.setattr(sys, "meta_path", [], raising=False)
    with pytest.raises(ModuleNotFoundError, match="pip install cleanlab"):
        find_label_errors(None)


def test_no_records():
    records = [
        TextClassificationRecord(text="test", prediction=[("mock", 0.0)]),
        TextClassificationRecord(text="test", annotation="test"),
    ]

    with pytest.raises(NoRecordsError, match="none of your records have a prediction AND annotation"):
        find_label_errors(records)


def test_multi_label_warning():
    record = TextClassificationRecord(
        text="test", prediction=[("mock", 0.0), ("mock2", 0.0)], annotation=["mock", "mock2"], multi_label=True
    )
    with pytest.warns(UserWarning, match="You provided the kwarg 'multi_label', but it is determined automatically"):
        find_label_errors([record], multi_label="True")


@pytest.mark.parametrize(
    "sort_by,expected",
    [
        ("likelihood", ("normalized_margin", "normalized_margin")),
        ("prediction", ("prob_given_label", "self_confidence")),
        ("none", (None, None)),
    ],
)
def test_sort_by(monkeypatch, sort_by, expected):
    if parse_version(cleanlab.__version__) < parse_version("2.0"):

        def mock_get_noise_indices(*args, **kwargs):
            assert kwargs["sorted_index_method"] == expected[0]
            return []

        monkeypatch.setattr(
            "cleanlab.pruning.get_noise_indices",
            mock_get_noise_indices,
        )
    else:

        def mock_find_label_issues(*args, **kwargs):
            assert kwargs["return_indices_ranked_by"] == expected[1]
            return []

        monkeypatch.setattr(
            "cleanlab.filter.find_label_issues",
            mock_find_label_issues,
        )

    record = TextClassificationRecord(text="mock", prediction=[("mock", 0.1)], annotation="mock")
    find_label_errors(records=[record], sort_by=sort_by)


def test_kwargs(monkeypatch, records):
    is_multi_label = records[0].multi_label

    if parse_version(cleanlab.__version__) < parse_version("2.0"):

        def mock_get_noise_indices(s, psx, n_jobs, **kwargs):
            assert kwargs == {
                "mock": "mock",
                "multi_label": is_multi_label,
                "sorted_index_method": "normalized_margin",
            }
            return []

        monkeypatch.setattr(
            "cleanlab.pruning.get_noise_indices",
            mock_get_noise_indices,
        )

        with pytest.raises(ValueError, match="'sorted_index_method' kwarg is not supported"):
            find_label_errors(records=records, sorted_index_method="mock")

        find_label_errors(records=records, mock="mock")
    else:

        def mock_find_label_issues(s, psx, n_jobs, **kwargs):
            assert kwargs == {
                "mock": "mock",
                "multi_label": is_multi_label,
                "return_indices_ranked_by": "normalized_margin" if not is_multi_label else "self_confidence",
            }
            return []

        monkeypatch.setattr(
            "cleanlab.filter.find_label_issues",
            mock_find_label_issues,
        )

        with pytest.raises(ValueError, match="'return_indices_ranked_by' kwarg is not supported"):
            find_label_errors(records=records, return_indices_ranked_by="mock")

        find_label_errors(records=records, mock="mock")


def test_construct_s_and_psx(records):
    import numpy as np

    s, psx = _construct_s_and_psx(records[:2])

    if records[0].multi_label:
        s_expected = np.array(
            [
                list([0]),
                list([0, 1]),
            ],
            dtype=object,
        )
        psx_expected = np.array(
            [
                [0.1, 0.9],
                [0.01, 0.9],
            ]
        )
    else:
        s_expected = np.array([1, 0])
        psx_expected = np.array(
            [
                [0.9, 0.1],
                [0.2, 0.8],
            ]
        )

    assert (s == s_expected).all()
    assert (psx == psx_expected).all()


def test_missing_predictions():
    records = [TextClassificationRecord(text="test", annotation="mock", prediction=[("mock2", 0.1)])]
    with pytest.raises(
        MissingPredictionError,
        match="It seems predictions are missing for the label 'mock'",
    ):
        _construct_s_and_psx(records)

    records.append(TextClassificationRecord(text="test", annotation="mock", prediction=[("mock", 0.1)]))
    with pytest.raises(
        MissingPredictionError,
        match="It seems a prediction for 'mock' is missing in the following record",
    ):
        _construct_s_and_psx(records)


@pytest.fixture
def dataset(argilla_user: User, records):
    dataset = "dataset_for_label_errors"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    log(records, name=dataset)

    yield dataset
    delete(dataset)


def test_find_label_errors_integration(argilla_user: User, dataset):
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    records = load(dataset)
    recs = find_label_errors(records)
    assert [rec.id for rec in recs] == [0, 10, 2, 4, 6, 8, 1, 11, 3, 5, 7, 9]
