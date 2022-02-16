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
import os
import sys
from time import sleep

import datasets
import pandas as pd
import pytest

import rubrix as rb
from rubrix.client.datasets import DatasetBase, WrongRecordTypeError
from rubrix.client.models import TextClassificationRecord

_HF_HUB_ACCESS_TOKEN = os.getenv("HF_HUB_ACCESS_TOKEN")


def test_init_NotImplementedError():
    with pytest.raises(NotImplementedError, match="has to define a `_RECORD_TYPE`"):
        DatasetBase()


def test_init(monkeypatch, singlelabel_textclassification_records):
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord
    )

    ds = DatasetBase(
        records=singlelabel_textclassification_records,
    )
    assert ds._records == singlelabel_textclassification_records

    ds = DatasetBase()
    assert ds._records == []

    with pytest.raises(WrongRecordTypeError, match="but you provided Text2TextRecord"):
        DatasetBase(
            records=[rb.Text2TextRecord(text="test")],
        )

    with pytest.raises(
        WrongRecordTypeError,
        match="various types: \['TextClassificationRecord', 'Text2TextRecord'\]",
    ):
        DatasetBase(
            records=[
                rb.TextClassificationRecord(inputs="test"),
                rb.Text2TextRecord(text="test"),
            ],
        )

    with pytest.raises(NotImplementedError):
        ds.to_datasets()

    with pytest.raises(NotImplementedError):
        ds._from_datasets("mock")

    with pytest.raises(NotImplementedError):
        ds._from_pandas("mock")


def test_to_dataframe(monkeypatch, singlelabel_textclassification_records):
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord
    )

    df = DatasetBase(singlelabel_textclassification_records).to_pandas()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert list(df.columns) == list(TextClassificationRecord.__fields__)


@pytest.mark.skip
def test_from_datasets(monkeypatch, caplog):
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord
    )
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._from_datasets", lambda x: x
    )

    ds = datasets.Dataset.from_dict({"unsupported_column": [None]})
    empty_ds = DatasetBase.from_datasets(ds)

    assert empty_ds.features == {}
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][1] == 30
    assert (
        "Following columns are not supported by the TextClassificationRecord model and are ignored: ['unsupported_column']"
        == caplog.record_tuples[0][2]
    )


def test_from_pandas(monkeypatch, caplog):
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord
    )
    monkeypatch.setattr("rubrix.client.datasets.DatasetBase._from_pandas", lambda x: x)

    df = pd.DataFrame({"unsupported_column": [None]})
    empty_df = DatasetBase.from_pandas(df)

    assert len(empty_df.columns) == 0
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][1] == 30
    assert (
        "Following columns are not supported by the TextClassificationRecord model and are ignored: ['unsupported_column']"
        == caplog.record_tuples[0][2]
    )


def test_to_datasets(monkeypatch, caplog):
    monkeypatch.setattr("rubrix.client.datasets.DatasetBase._RECORD_TYPE", "mock")
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._to_datasets_dict",
        lambda x: {"metadata": [{"int_or_str": 1}, {"int_or_str": "str"}]},
    )

    ds = DatasetBase()
    datasets_ds = ds.to_datasets()
    assert datasets_ds.features == {}
    assert len(datasets_ds) == 0
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][1] == 30
    assert "The 'metadata' of the records were removed" in caplog.record_tuples[0][2]


def test_datasets_not_installed(monkeypatch):
    monkeypatch.setattr("rubrix.client.datasets.DatasetBase._RECORD_TYPE", "mock")
    monkeypatch.setitem(sys.modules, "datasets", None)
    with pytest.raises(ModuleNotFoundError, match="pip install datasets>1.17.0"):
        DatasetBase().to_datasets()


def test_datasets_wrong_version(monkeypatch):
    monkeypatch.setattr("rubrix.client.datasets.DatasetBase._RECORD_TYPE", "mock")
    monkeypatch.setattr("datasets.__version__", "1.16.0")
    with pytest.raises(ModuleNotFoundError, match="pip install -U datasets>1.17.0"):
        DatasetBase().to_datasets()


def test_iter_len_getitem(monkeypatch, singlelabel_textclassification_records):
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord
    )
    dataset = DatasetBase(singlelabel_textclassification_records)

    for record, expected in zip(dataset, singlelabel_textclassification_records):
        assert record == expected

    assert len(dataset) == 5
    assert dataset[1] is singlelabel_textclassification_records[1]


def test_setitem_delitem(monkeypatch, singlelabel_textclassification_records):
    monkeypatch.setattr(
        "rubrix.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord
    )
    dataset = DatasetBase(
        [rec.copy(deep=True) for rec in singlelabel_textclassification_records],
    )

    record = rb.TextClassificationRecord(inputs="mock")
    dataset[0] = record

    assert dataset._records[0] is record

    assert len(dataset) == 5
    del dataset[1]
    assert len(dataset) == 4

    with pytest.raises(
        WrongRecordTypeError,
        match="You are only allowed to set a record of type .*TextClassificationRecord.* but you provided .*Text2TextRecord.*",
    ):
        dataset[0] = rb.Text2TextRecord(text="mock")


class TestDatasetForTextClassification:
    def test_init(self, singlelabel_textclassification_records):
        ds = rb.DatasetForTextClassification(singlelabel_textclassification_records)
        assert ds._RECORD_TYPE == rb.TextClassificationRecord
        assert ds._records == singlelabel_textclassification_records

    @pytest.mark.parametrize(
        "records",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_to_from_datasets(self, records, request):
        records = request.getfixturevalue(records)
        expected_dataset = rb.DatasetForTextClassification(records)

        dataset_ds = expected_dataset.to_datasets()

        assert isinstance(dataset_ds, datasets.Dataset)
        assert dataset_ds.column_names == list(expected_dataset[0].__fields__.keys())
        assert dataset_ds.features["prediction"] == [
            {"label": datasets.Value("string"), "score": datasets.Value("float64")}
        ]

        dataset = rb.DatasetForTextClassification.from_datasets(dataset_ds)

        assert isinstance(dataset, rb.DatasetForTextClassification)
        _compare_datasets(dataset, expected_dataset)

        missing_optional_cols = datasets.Dataset.from_dict({"inputs": ["mock"]})
        rec = rb.DatasetForTextClassification.from_datasets(missing_optional_cols)[0]
        assert rec.inputs == {"text": "mock"}

    def test_from_to_datasets_id(self):
        dataset_rb = rb.DatasetForTextClassification(
            [rb.TextClassificationRecord(inputs="mock")]
        )
        dataset_ds = dataset_rb.to_datasets()
        assert dataset_ds["id"] == [None]

        assert rb.read_datasets(dataset_ds, task="TextClassification")[0].id is None

    def test_datasets_empty_metadata(self):
        dataset = rb.DatasetForTextClassification(
            [rb.TextClassificationRecord(inputs="mock")]
        )
        assert dataset.to_datasets()["metadata"] == [None]

    @pytest.mark.parametrize(
        "records",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_to_from_pandas(self, records, request):
        records = request.getfixturevalue(records)
        expected_dataset = rb.DatasetForTextClassification(records)

        dataset_df = expected_dataset.to_pandas()

        assert isinstance(dataset_df, pd.DataFrame)
        assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

        dataset = rb.DatasetForTextClassification.from_pandas(dataset_df)

        assert isinstance(dataset, rb.DatasetForTextClassification)
        for rec, expected in zip(dataset, expected_dataset):
            assert rec == expected

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    @pytest.mark.parametrize(
        "records",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_push_to_hub(self, request, records):
        records = request.getfixturevalue(records)
        dataset_rb = rb.DatasetForTextClassification(records)
        dataset_rb.to_datasets().push_to_hub(
            "rubrix/_test_text_classification_records",
            token=_HF_HUB_ACCESS_TOKEN,
            private=True,
        )
        sleep(1)
        dataset_ds = datasets.load_dataset(
            "rubrix/_test_text_classification_records",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )

        assert isinstance(dataset_ds, datasets.Dataset)

    @pytest.mark.parametrize(
        "records",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_prepare_for_training(self, request, records):
        records = request.getfixturevalue(records)

        ds = rb.DatasetForTextClassification(records)
        train = ds.prepare_for_training()

        assert isinstance(train, datasets.Dataset)
        assert train.column_names == ["text", "context", "label"]
        assert len(train) == 2
        assert train[1]["text"] == "mock3"
        assert train[1]["context"] == "mock3"
        assert train.features["text"] == datasets.Value("string")
        if records[0].multi_label:
            assert train.features["label"] == [datasets.ClassLabel(names=["a", "b"])]
        else:
            assert train.features["label"] == datasets.ClassLabel(names=["a"])


class TestDatasetForTokenClassification:
    def test_init(self, tokenclassification_records):
        ds = rb.DatasetForTokenClassification(tokenclassification_records)
        assert ds._RECORD_TYPE == rb.TokenClassificationRecord
        assert ds._records == tokenclassification_records

    def test_to_from_datasets(self, tokenclassification_records):
        expected_dataset = rb.DatasetForTokenClassification(tokenclassification_records)

        dataset_ds = expected_dataset.to_datasets()

        assert isinstance(dataset_ds, datasets.Dataset)
        assert dataset_ds.column_names == list(expected_dataset[0].__fields__.keys())
        assert dataset_ds.features["prediction"] == [
            {
                "label": datasets.Value("string"),
                "start": datasets.Value("int64"),
                "end": datasets.Value("int64"),
                "score": datasets.Value("float64"),
            }
        ]
        assert dataset_ds.features["annotation"] == [
            {
                "label": datasets.Value("string"),
                "start": datasets.Value("int64"),
                "end": datasets.Value("int64"),
            }
        ]

        dataset = rb.DatasetForTokenClassification.from_datasets(dataset_ds)

        assert isinstance(dataset, rb.DatasetForTokenClassification)
        _compare_datasets(dataset, expected_dataset)

        missing_optional_cols = datasets.Dataset.from_dict(
            {"text": ["mock"], "tokens": [["mock"]]}
        )
        rec = rb.DatasetForTokenClassification.from_datasets(missing_optional_cols)[0]
        assert rec.text == "mock" and rec.tokens == ["mock"]

    def test_from_to_datasets_id(self):
        dataset_rb = rb.DatasetForTokenClassification(
            [rb.TokenClassificationRecord(text="mock", tokens=["mock"])]
        )
        dataset_ds = dataset_rb.to_datasets()
        assert dataset_ds["id"] == [None]

        assert rb.read_datasets(dataset_ds, task="TokenClassification")[0].id is None

    def test_datasets_empty_metadata(self):
        dataset = rb.DatasetForTokenClassification(
            [rb.TokenClassificationRecord(text="mock", tokens=["mock"])]
        )
        assert dataset.to_datasets()["metadata"] == [None]

    def test_to_from_pandas(self, tokenclassification_records):
        expected_dataset = rb.DatasetForTokenClassification(tokenclassification_records)

        dataset_df = expected_dataset.to_pandas()

        assert isinstance(dataset_df, pd.DataFrame)
        assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

        dataset = rb.DatasetForTokenClassification.from_pandas(dataset_df)

        assert isinstance(dataset, rb.DatasetForTokenClassification)
        for rec, expected in zip(dataset, expected_dataset):
            assert rec == expected

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_push_to_hub(self, tokenclassification_records):
        dataset_rb = rb.DatasetForTokenClassification(tokenclassification_records)
        dataset_rb.to_datasets().push_to_hub(
            "rubrix/_test_token_classification_records",
            token=_HF_HUB_ACCESS_TOKEN,
            private=True,
        )
        sleep(1)
        dataset_ds = datasets.load_dataset(
            "rubrix/_test_token_classification_records",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )

        assert isinstance(dataset_ds, datasets.Dataset)


class TestDatasetForText2Text:
    def test_init(self, text2text_records):
        ds = rb.DatasetForText2Text(text2text_records)
        assert ds._RECORD_TYPE == rb.Text2TextRecord
        assert ds._records == text2text_records

    def test_to_from_datasets(self, text2text_records):
        expected_dataset = rb.DatasetForText2Text(text2text_records)

        dataset_ds = expected_dataset.to_datasets()

        assert isinstance(dataset_ds, datasets.Dataset)
        assert dataset_ds.column_names == list(expected_dataset[0].__fields__.keys())
        assert dataset_ds.features["prediction"] == [
            {
                "text": datasets.Value("string"),
                "score": datasets.Value("float64"),
            }
        ]

        dataset = rb.DatasetForText2Text.from_datasets(dataset_ds)

        assert isinstance(dataset, rb.DatasetForText2Text)
        _compare_datasets(dataset, expected_dataset)

        missing_optional_cols = datasets.Dataset.from_dict({"text": ["mock"]})
        rec = rb.DatasetForText2Text.from_datasets(missing_optional_cols)[0]
        assert rec.text == "mock"

        # alternative format for the predictions
        ds = datasets.Dataset.from_dict(
            {"text": ["example"], "prediction": [["ejemplo"]]}
        )
        rec = rb.DatasetForText2Text.from_datasets(ds)[0]
        assert rec.prediction[0][0] == "ejemplo"
        assert rec.prediction[0][1] == pytest.approx(1.0)

    def test_from_to_datasets_id(self):
        dataset_rb = rb.DatasetForText2Text([rb.Text2TextRecord(text="mock")])
        dataset_ds = dataset_rb.to_datasets()
        assert dataset_ds["id"] == [None]

        assert rb.read_datasets(dataset_ds, task="Text2Text")[0].id is None

    def test_datasets_empty_metadata(self):
        dataset = rb.DatasetForText2Text([rb.Text2TextRecord(text="mock")])
        assert dataset.to_datasets()["metadata"] == [None]

    def test_to_from_pandas(self, text2text_records):
        expected_dataset = rb.DatasetForText2Text(text2text_records)

        dataset_df = expected_dataset.to_pandas()

        assert isinstance(dataset_df, pd.DataFrame)
        assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

        dataset = rb.DatasetForText2Text.from_pandas(dataset_df)

        assert isinstance(dataset, rb.DatasetForText2Text)
        for rec, expected in zip(dataset, expected_dataset):
            assert rec == expected

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_push_to_hub(self, text2text_records):
        dataset_rb = rb.DatasetForText2Text(text2text_records)
        dataset_rb.to_datasets().push_to_hub(
            "rubrix/_test_text2text_records",
            token=_HF_HUB_ACCESS_TOKEN,
            private=True,
        )
        sleep(1)
        dataset_ds = datasets.load_dataset(
            "rubrix/_test_text2text_records",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )

        assert isinstance(dataset_ds, datasets.Dataset)


def _compare_datasets(dataset, expected_dataset):
    for rec, expected in zip(dataset, expected_dataset):
        for col in expected.__fields__.keys():
            # TODO: have to think about how we deal with `None`s
            if col in ["metadata", "metrics"]:
                continue
            assert getattr(rec, col) == getattr(expected, col)


@pytest.mark.parametrize(
    "task,dataset_class",
    [
        ("TextClassification", "DatasetForTextClassification"),
        ("TokenClassification", "DatasetForTokenClassification"),
        ("Text2Text", "DatasetForText2Text"),
    ],
)
def test_read_pandas(monkeypatch, task, dataset_class):
    def mock_from_pandas(mock):
        return mock

    monkeypatch.setattr(
        f"rubrix.client.datasets.{dataset_class}.from_pandas", mock_from_pandas
    )

    assert rb.read_pandas("mock", task) == "mock"


@pytest.mark.parametrize(
    "task,dataset_class",
    [
        ("TextClassification", "DatasetForTextClassification"),
        ("TokenClassification", "DatasetForTokenClassification"),
        ("Text2Text", "DatasetForText2Text"),
    ],
)
def test_read_datasets(monkeypatch, task, dataset_class):
    def mock_from_datasets(mock):
        return mock

    monkeypatch.setattr(
        f"rubrix.client.datasets.{dataset_class}.from_datasets", mock_from_datasets
    )

    assert rb.read_datasets("mock", task) == "mock"
