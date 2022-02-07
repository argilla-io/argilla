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
from typing import List

import datasets
import pandas as pd
import pytest

import rubrix as rb
from rubrix.client.dataset import MixedRecordTypesError, WrongRecordTypeError


def test_init(singlelabel_textclassification_records):
    dataset = rb.Dataset()

    assert dataset._records == []
    assert dataset._record_type is None

    dataset = rb.Dataset(singlelabel_textclassification_records)

    assert dataset._records is singlelabel_textclassification_records
    assert dataset._record_type is type(singlelabel_textclassification_records[0])

    with pytest.raises(
        MixedRecordTypesError,
        match="but you provided more than one: .*TextClassificationRecord.*Text2TextRecord.*",
    ):
        rb.Dataset(
            [
                rb.TextClassificationRecord(inputs="mock"),
                rb.Text2TextRecord(text="mock"),
            ]
        )


def test_iter_len_getitem(singlelabel_textclassification_records):
    dataset = rb.Dataset(singlelabel_textclassification_records)

    for record, expected in zip(dataset, singlelabel_textclassification_records):
        assert record == expected

    assert len(dataset) == 4
    assert dataset[1] is singlelabel_textclassification_records[1]


def test_setitem_delitem(singlelabel_textclassification_records):
    dataset = rb.Dataset(singlelabel_textclassification_records)

    record = rb.TextClassificationRecord(inputs="mock")
    dataset[0] = record

    assert dataset._records[0] is record

    assert len(dataset) == 4
    del dataset[1]
    assert len(dataset) == 3

    with pytest.raises(
        WrongRecordTypeError,
        match="You are only allowed to set a record of type .*TextClassificationRecord.* but you provided .*Text2TextRecord.*",
    ):
        dataset[0] = rb.Text2TextRecord(text="mock")


def test_append(singlelabel_textclassification_records):
    dataset = rb.Dataset()
    record = rb.TextClassificationRecord(inputs="mock")

    dataset.append(record)

    assert dataset._record_type == type(record)
    assert dataset._records[-1] is record

    with pytest.raises(
        WrongRecordTypeError,
        match="You are only allowed to append a record of type .*TextClassificationRecord.* but you provided .*Text2TextRecord.*",
    ):
        dataset.append(rb.Text2TextRecord(text="mock"))


@pytest.mark.parametrize(
    "records",
    ["singlelabel_textclassification_records", "multilabel_textclassification_records"],
)
def test_to_from_datasets_textclassification(records, request):
    records = request.getfixturevalue(records)
    expected_dataset = rb.Dataset(records)

    dataset_ds = expected_dataset.to_datasets()

    assert isinstance(dataset_ds, datasets.Dataset)
    assert dataset_ds.column_names == list(expected_dataset[0].__fields__.keys())
    assert dataset_ds.features["prediction"] == [
        {"label": datasets.Value("string"), "score": datasets.Value("float64")}
    ]

    dataset = rb.Dataset.from_datasets(dataset_ds, task="TextClassification")

    assert isinstance(dataset, rb.Dataset)
    for rec, expected in zip(dataset, expected_dataset):
        for col in expected.__fields__.keys():
            # TODO: have to think about how we deal with `None`s
            if col in ["metadata", "metrics"]:
                continue
            assert getattr(rec, col) == getattr(expected, col)


def test_to_from_datasets_tokenclassification(tokenclassification_records):
    expected_dataset = rb.Dataset(tokenclassification_records)

    dataset_ds = expected_dataset.to_datasets()

    assert isinstance(dataset_ds, datasets.Dataset)
    assert dataset_ds.column_names == list(expected_dataset[0].__fields__.keys())
    assert dataset_ds.features["prediction"] == [
        {
            "label": datasets.Value("string"),
            "start": datasets.Value("int64"),
            "end": datasets.Value("int64"),
        }
    ]
    assert dataset_ds.features["annotation"] == [
        {
            "label": datasets.Value("string"),
            "start": datasets.Value("int64"),
            "end": datasets.Value("int64"),
        }
    ]

    dataset = rb.Dataset.from_datasets(dataset_ds, task="TokenClassification")

    assert isinstance(dataset, rb.Dataset)
    for rec, expected in zip(dataset, expected_dataset):
        for col in expected.__fields__.keys():
            # TODO: have to think about how we deal with `None`s
            if col in ["metadata", "metrics"]:
                continue
            assert getattr(rec, col) == getattr(expected, col)


@pytest.mark.parametrize(
    "records",
    ["singlelabel_textclassification_records", "multilabel_textclassification_records"],
)
def test_to_from_pandas_textclassification(records, request):
    records = request.getfixturevalue(records)
    expected_dataset = rb.Dataset(records)

    dataset_df = expected_dataset.to_pandas()

    assert isinstance(dataset_df, pd.DataFrame)
    assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

    dataset = rb.Dataset.from_pandas(dataset_df, task="TextClassification")

    assert isinstance(dataset, rb.Dataset)
    for rec, expected in zip(dataset, expected_dataset):
        assert rec == expected


def test_to_from_pandas_tokenclassification(tokenclassification_records):
    expected_dataset = rb.Dataset(tokenclassification_records)

    dataset_df = expected_dataset.to_pandas()

    assert isinstance(dataset_df, pd.DataFrame)
    assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

    dataset = rb.Dataset.from_pandas(dataset_df, task="TokenClassification")

    assert isinstance(dataset, rb.Dataset)
    for rec, expected in zip(dataset, expected_dataset):
        assert rec == expected
