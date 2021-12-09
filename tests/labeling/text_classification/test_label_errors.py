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

import pytest

import rubrix as rb
from rubrix.labeling.text_classification import find_label_errors
from rubrix.labeling.text_classification.label_errors import NoRecordsError, SortBy
from tests.server.test_helpers import client, mocking_client


def test_sort_by():
    with pytest.raises(ValueError, match="mock is not a valid SortBy"):
        SortBy("mock")


def test_not_installed(monkeypatch):
    monkeypatch.setitem(sys.modules, "cleanlab", None)
    with pytest.raises(ModuleNotFoundError, match="pip install cleanlab"):
        find_label_errors(None)


def test_no_records():
    records = [
        rb.TextClassificationRecord(inputs="test", prediction=[("mock", 0.0)]),
        rb.TextClassificationRecord(inputs="test", annotation="test"),
    ]

    with pytest.raises(
        NoRecordsError, match="none of your records have a prediction AND annotation"
    ):
        find_label_errors(records)


def test_multi_label_warning(caplog):
    record = rb.TextClassificationRecord(
        inputs="test", prediction=[("mock", 0.0)], annotation="mock"
    )
    find_label_errors([record], multi_label="True")
    assert (
        "You provided the kwarg 'multi_label', but it is determined automatically"
        in caplog.text
    )


@pytest.mark.parametrize(
    "sort_by,expected",
    [
        ("likelihood", "normalized_margin"),
        ("prediction", "prob_given_label"),
        ("none", None),
    ],
)
def test_sort_by(monkeypatch, sort_by, expected):
    def mock_get_noise_indices(*args, **kwargs):
        assert kwargs["sorted_index_method"] == expected
        return []

    monkeypatch.setattr(
        "cleanlab.pruning.get_noise_indices",
        mock_get_noise_indices,
    )

    record = rb.TextClassificationRecord(
        inputs="mock", prediction=[("mock", 0.1)], annotation="mock"
    )
    find_label_errors(records=[record], sort_by=sort_by)

    with pytest.raises(
        ValueError, match="'sorted_index_method' kwarg is not supported"
    ):
        find_label_errors(records=[record], sorted_index_method="mock")


@pytest.fixture(params=[False, True], ids=["single_label", "multi_label"])
def dataset(request, monkeypatch):
    mocking_client(monkeypatch, client)

    dataset = "dataset_for_label_errors"

    if not request.param:
        records = [
            rb.TextClassificationRecord(
                inputs="test", annotation=anot, prediction=pred, id=i
            )
            for i, anot, pred in zip(
                range(2 * 6),
                ["good", "bad"] * 6,
                [[("bad", 0.9), ("good", 0.1)], [("good", 0.8), ("bad", 0.2)]] * 6,
            )
        ]
    else:
        records = [
            rb.TextClassificationRecord(
                inputs="test", annotation=anot, prediction=pred, multi_label=True, id=i
            )
            for i, anot, pred in zip(
                range(2 * 6),
                [["bad"], ["bad", "good"]] * 6,
                [[("bad", 0.1), ("good", 0.9)], [("good", 0.6), ("bad", 0.05)]] * 6,
            )
        ]

    rb.log(records, name=dataset)
    yield dataset
    rb.delete(dataset)


def test_find_label_errors_integration(dataset):
    records = rb.load(dataset, as_pandas=False)
    recs = find_label_errors(records)
    assert [rec.id for rec in recs] == list(range(0, 11, 2)) + list(range(1, 12, 2))
