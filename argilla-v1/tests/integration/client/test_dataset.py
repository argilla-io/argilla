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
import copy
import os
import sys
from time import sleep

import datasets
import pandas as pd
import pytest
import spacy
from argilla_v1.client.datasets import (
    DatasetBase,
    DatasetForText2Text,
    DatasetForTextClassification,
    DatasetForTokenClassification,
    WrongRecordTypeError,
    read_datasets,
    read_pandas,
)
from argilla_v1.client.models import (
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from argilla_v1.datasets import TextClassificationSettings

_HF_HUB_ACCESS_TOKEN = os.getenv("HF_HUB_ACCESS_TOKEN")


def _push_to_hub_with_retries(ds: datasets.Dataset, retries: int = 3, **kwargs):
    try:
        return ds.push_to_hub(**kwargs)
    except Exception as ex:
        print(f"Found error pushing dataset with params {kwargs}. Error: {ex}")
        if retries == 0:
            print("No more retries will be done. Exiting...")
        else:
            print(f" Retring {retries} more times")
        return _push_to_hub_with_retries(ds, retries=retries - 1, **kwargs)


class TestDatasetBase:
    def test_init_NotImplementedError(self):
        with pytest.raises(NotImplementedError, match="has to define a `_RECORD_TYPE`"):
            DatasetBase()

    def test_init(self, monkeypatch, singlelabel_textclassification_records):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord)

        ds = DatasetBase(
            records=singlelabel_textclassification_records,
        )
        assert ds._records == singlelabel_textclassification_records

        ds = DatasetBase()
        assert ds._records == []

        with pytest.raises(WrongRecordTypeError, match="but you provided Text2TextRecord"):
            DatasetBase(
                records=[Text2TextRecord(text="test")],
            )

        with pytest.raises(
            WrongRecordTypeError,
            match=r"various types: \['TextClassificationRecord', 'Text2TextRecord'\]",
        ):
            DatasetBase(
                records=[
                    TextClassificationRecord(text="test"),
                    Text2TextRecord(text="test"),
                ],
            )

        with pytest.raises(NotImplementedError):
            ds.to_datasets()

        with pytest.raises(NotImplementedError):
            ds.from_datasets("mock")

        with pytest.raises(NotImplementedError):
            ds._from_pandas("mock")

    def test_to_dataframe(self, monkeypatch, singlelabel_textclassification_records):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord)

        df = DatasetBase(singlelabel_textclassification_records).to_pandas()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == list(TextClassificationRecord.__fields__)

    def test_prepare_dataset_and_column_mapping(self, monkeypatch):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord)

        ds = datasets.Dataset.from_dict(
            {"unsupported_column": [None], "ID": [1], "inputs_a": ["a"], "inputs_b": ["b"], "metadata": ["mock"]}
        )

        ds_dict = datasets.DatasetDict(train=ds)
        with pytest.raises(ValueError, match="datasets.DatasetDict` are not supported"):
            DatasetBase._prepare_dataset_and_column_mapping(ds_dict, None)

        col_mapping = dict(id="ID", inputs=["inputs_a", "inputs_b"], metadata="metadata")

        with pytest.warns(
            UserWarning,
            match=r"Following columns are not supported by the TextClassificationRecord model "
            r"and are ignored: \['unsupported_column'\]",
        ):
            prepared_ds, col_to_be_joined = DatasetBase._prepare_dataset_and_column_mapping(ds, col_mapping)

            assert prepared_ds.column_names == ["id", "inputs_a", "inputs_b", "metadata"]
            assert col_to_be_joined == {"inputs": ["inputs_a", "inputs_b"], "metadata": ["metadata"]}

    def test_from_pandas(self, monkeypatch):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord)
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._from_pandas", lambda x: x)

        df = pd.DataFrame({"unsupported_column": [None]})

        with pytest.warns(
            UserWarning,
            match="Following columns are not supported by the "
            r"TextClassificationRecord model and are ignored: \['unsupported_column'\]",
        ):
            empty_df = DatasetBase.from_pandas(df)
            assert len(empty_df.columns) == 0

    def test_to_datasets(self, monkeypatch):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", "mock")
        monkeypatch.setattr(
            "argilla_v1.client.datasets.DatasetBase._to_datasets_dict",
            lambda x: {"metadata": [{"int_or_str": 1}, {"int_or_str": "str"}]},
        )

        ds = DatasetBase()
        with pytest.warns(UserWarning, match="The 'metadata' of the records were removed"):
            datasets_ds = ds.to_datasets()
            assert datasets_ds.features == {}
            assert len(datasets_ds) == 0

    def test_datasets_not_installed(self, monkeypatch):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", "mock")
        monkeypatch.setattr(sys, "meta_path", [], raising=False)
        with pytest.raises(ModuleNotFoundError, match="pip install datasets>1.17.0"):
            DatasetBase().to_datasets()

    def test_iter_len_getitem(self, monkeypatch, singlelabel_textclassification_records):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord)
        dataset = DatasetBase(singlelabel_textclassification_records)

        for record, expected in zip(dataset, singlelabel_textclassification_records):
            assert record == expected

        assert len(dataset) == 5
        assert dataset[1] is singlelabel_textclassification_records[1]

    def test_setitem_delitem(self, monkeypatch, singlelabel_textclassification_records):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord)
        dataset = DatasetBase(
            [rec.copy(deep=True) for rec in singlelabel_textclassification_records],
        )

        record = TextClassificationRecord(text="mock")
        dataset[0] = record

        assert dataset._records[0] is record

        assert len(dataset) == 5
        del dataset[1]
        assert len(dataset) == 4

        with pytest.raises(
            WrongRecordTypeError,
            match=(
                "You are only allowed to set a record of type"
                " .*TextClassificationRecord.* but you provided .*Text2TextRecord.*"
            ),
        ):
            dataset[0] = Text2TextRecord(text="mock")

    def test_prepare_for_training_train_test_splits(self, monkeypatch, singlelabel_textclassification_records):
        monkeypatch.setattr("argilla_v1.client.datasets.DatasetBase._RECORD_TYPE", TextClassificationRecord)
        temp_records = copy.deepcopy(singlelabel_textclassification_records)
        settings = TextClassificationSettings(["a", "b", "c"])
        ds = DatasetBase(temp_records)

        with pytest.raises(
            AssertionError,
            match="`train_size` and `test_size` must be larger than 0.",
        ):
            ds.prepare_for_training(train_size=-1, settings=settings)

        with pytest.raises(AssertionError, match="`train_size` and `test_size` must sum to 1."):
            ds.prepare_for_training(test_size=0.1, train_size=0.6, settings=settings)

        for rec in ds:
            rec.annotation = None
        with pytest.raises(AssertionError, match="Dataset has no annotations."):
            ds.prepare_for_training(settings=settings)


class TestDatasetForTextClassification:
    def test_init(self, singlelabel_textclassification_records):
        ds = DatasetForTextClassification(singlelabel_textclassification_records)
        assert ds._RECORD_TYPE == TextClassificationRecord
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
        expected_dataset = DatasetForTextClassification(records)

        expected_dataset.prepare_for_training(train_size=0.5)
        dataset_ds = expected_dataset.to_datasets()

        assert isinstance(dataset_ds, datasets.Dataset)

        assert dataset_ds.column_names == [
            "text",
            "inputs",
            "prediction",
            "prediction_agent",
            "annotation",
            "annotation_agent",
            "vectors",
            "multi_label",
            "explanation",
            "id",
            "metadata",
            "status",
            "event_timestamp",
            "metrics",
        ]
        assert dataset_ds.features["prediction"] == [
            {
                "label": datasets.Value("string"),
                "score": datasets.Value("float64"),
            }
        ]

        dataset = DatasetForTextClassification.from_datasets(dataset_ds)

        assert isinstance(dataset, DatasetForTextClassification)
        _compare_datasets(dataset, expected_dataset)

        missing_optional_cols = datasets.Dataset.from_dict({"inputs": ["mock"]})
        rec = DatasetForTextClassification.from_datasets(missing_optional_cols)[0]
        assert rec.inputs == {"text": "mock"}

    def test_from_to_datasets_id(self):
        record = TextClassificationRecord(text="mock")
        dataset_rb = DatasetForTextClassification([record])
        dataset_ds = dataset_rb.to_datasets()
        assert dataset_ds["id"] == [record.id]

        assert read_datasets(dataset_ds, task="TextClassification")[0].id == record.id

    def test_datasets_empty_metadata(self):
        record = TextClassificationRecord(text="mock")
        dataset = DatasetForTextClassification([record])
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
        expected_dataset = DatasetForTextClassification(records)

        dataset_df = expected_dataset.to_pandas()

        assert isinstance(dataset_df, pd.DataFrame)
        assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

        dataset = DatasetForTextClassification.from_pandas(dataset_df)

        assert isinstance(dataset, DatasetForTextClassification)
        for rec, expected in zip(dataset, expected_dataset):
            assert rec == expected

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    @pytest.mark.parametrize(
        "name",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_push_to_hub(self, request, name: str):
        records = request.getfixturevalue(name)
        # TODO(@frascuchon): move dataset to new organization
        dataset_name = f"rubrix/_test_text_classification_records-{name}"
        dataset_ds = DatasetForTextClassification(records).to_datasets()
        _push_to_hub_with_retries(dataset_ds, repo_id=dataset_name, token=_HF_HUB_ACCESS_TOKEN, private=True)
        sleep(1)
        dataset_ds = datasets.load_dataset(
            dataset_name,
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

        ds = DatasetForTextClassification(records)
        train = ds.prepare_for_training(seed=42)

        if not ds[0].multi_label:
            column_names = ["id", "text", "label"]
        else:
            column_names = ["id", "text", "label", "binarized_label"]

        assert isinstance(train, datasets.Dataset)
        assert train.column_names == column_names
        assert len(train) == 2
        assert train[1]["text"] == "mock3"
        assert train.features["text"] == datasets.Value("string")
        if records[0].multi_label:
            assert train.features["label"] == [datasets.ClassLabel(names=["a", "b"])]
        else:
            assert train.features["label"] == datasets.ClassLabel(names=["a"])

        train_test = ds.prepare_for_training(train_size=0.5, seed=42)
        assert len(train_test["train"]) == 1
        assert len(train_test["test"]) == 1
        for split in ["train", "test"]:
            assert set(train_test[split].column_names) == set(column_names)

    @pytest.mark.parametrize(
        "records",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_prepare_for_training_with_spacy(self, request, records):
        records = request.getfixturevalue(records)

        ds = DatasetForTextClassification(records)
        with pytest.raises(ValueError):
            train = ds.prepare_for_training(framework="spacy", seed=42)
        nlp = spacy.blank("en")
        doc_bin = ds.prepare_for_training(framework="spacy", lang=nlp, seed=42)

        assert isinstance(doc_bin, spacy.tokens.DocBin)
        docs = list(doc_bin.get_docs(nlp.vocab))
        assert len(docs) == 2

        if records[0].multi_label:
            assert set(list(docs[0].cats.keys())) == set(["a", "b"])
        else:
            assert isinstance(docs[0].cats, dict)

        train, test = ds.prepare_for_training(train_size=0.5, framework="spacy", lang=nlp, seed=42)
        docs_train = list(train.get_docs(nlp.vocab))
        docs_test = list(train.get_docs(nlp.vocab))
        assert len(list(docs_train)) == 1
        assert len(list(docs_test)) == 1
        assert "id" in docs_train[0].user_data
        assert "id" in docs_test[0].user_data

    @pytest.mark.parametrize(
        "records",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_prepare_for_training_with_openai(self, request, records):
        records = request.getfixturevalue(records)
        ds = DatasetForTextClassification(records)
        jsonl = ds.prepare_for_training(framework="openai", seed=42)

        assert isinstance(jsonl, list)
        assert isinstance(jsonl[0], dict)
        assert "prompt" in jsonl[0] and "completion" in jsonl[0] and "id" in jsonl[0]

    @pytest.mark.parametrize(
        "records",
        [
            "singlelabel_textclassification_records",
            "multilabel_textclassification_records",
        ],
    )
    def test_prepare_for_training_with_spark_nlp(self, request, records):
        records = request.getfixturevalue(records)

        ds = DatasetForTextClassification(records)
        df = ds.prepare_for_training("spark-nlp", train_size=1, seed=42)

        if ds[0].multi_label:
            column_names = ["id", "text", "labels"]
        else:
            column_names = ["id", "text", "label"]

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == column_names
        assert len(df) == 2

        df_train, df_test = ds.prepare_for_training("spark-nlp", train_size=0.5, seed=42)
        assert len(df_train) == 1
        assert len(df_test) == 1
        assert isinstance(df_train, pd.DataFrame)
        assert isinstance(df_test, pd.DataFrame)
        assert list(df_train.columns) == column_names
        assert list(df_test.columns) == column_names

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_from_dataset_with_non_argilla_format_multilabel(self):
        ds = datasets.load_dataset(
            "argilla/_go_emotions_test_100",
            split="test",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
        )

        rb_ds = DatasetForTextClassification.from_datasets(
            ds,
            inputs="id",
            annotation="labels",
        )
        assert rb_ds[0].inputs == {"id": "eecwqtt"}

        rb_ds = DatasetForTextClassification.from_datasets(
            ds,
            text="text",
            annotation="labels",
        )
        again_the_ds = rb_ds.to_datasets()
        assert again_the_ds.column_names == [
            "text",
            "inputs",
            "prediction",
            "prediction_agent",
            "annotation",
            "annotation_agent",
            "vectors",
            "multi_label",
            "explanation",
            "id",
            "metadata",
            "status",
            "event_timestamp",
            "metrics",
        ]

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_from_dataset_with_non_argilla_format(self):
        ds = datasets.load_dataset(
            "argilla/_app_reviews_train_100",
            split="train",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
        )

        rb_ds = DatasetForTextClassification.from_datasets(
            ds, text="review", annotation="star", metadata=["package_name", "date"]
        )

        again_the_ds = rb_ds.to_datasets()
        assert again_the_ds.column_names == [
            "text",
            "inputs",
            "prediction",
            "prediction_agent",
            "annotation",
            "annotation_agent",
            "vectors",
            "multi_label",
            "explanation",
            "id",
            "metadata",
            "status",
            "event_timestamp",
            "metrics",
        ]

    def test_from_datasets_with_annotation_arg(self):
        dataset_ds = datasets.Dataset.from_dict(
            {"text": ["mock", "mock2"], "label": [0, -1]},
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "label": datasets.ClassLabel(names=["HAM"]),
                }
            ),
        )
        dataset_rb = DatasetForTextClassification.from_datasets(dataset_ds, annotation="label")

        assert [rec.annotation for rec in dataset_rb] == ["HAM", None]


class TestDatasetForTokenClassification:
    def test_init(self, tokenclassification_records):
        ds = DatasetForTokenClassification(tokenclassification_records)
        assert ds._RECORD_TYPE == TokenClassificationRecord
        assert ds._records == tokenclassification_records

    def test_to_from_datasets(self, tokenclassification_records):
        expected_dataset = DatasetForTokenClassification(tokenclassification_records)

        dataset_ds = expected_dataset.to_datasets()

        print(dataset_ds.column_names)

        assert isinstance(dataset_ds, datasets.Dataset)
        assert dataset_ds.column_names == [
            "text",
            "tokens",
            "prediction",
            "prediction_agent",
            "annotation",
            "annotation_agent",
            "vectors",
            "id",
            "metadata",
            "status",
            "event_timestamp",
            "metrics",
        ]
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

        dataset = DatasetForTokenClassification.from_datasets(dataset_ds)

        assert isinstance(dataset, DatasetForTokenClassification)
        _compare_datasets(dataset, expected_dataset)

        missing_optional_cols = datasets.Dataset.from_dict({"text": ["mock"], "tokens": [["mock"]]})
        rec = DatasetForTokenClassification.from_datasets(missing_optional_cols)[0]
        assert rec.text == "mock" and rec.tokens == ["mock"]

    def test_from_to_datasets_id(self):
        record = TokenClassificationRecord(text="mock", tokens=["mock"])
        dataset_rb = DatasetForTokenClassification([record])
        dataset_ds = dataset_rb.to_datasets()
        assert dataset_ds["id"] == [record.id]

        assert read_datasets(dataset_ds, task="TokenClassification")[0].id == record.id

    def test_prepare_for_training_empty(self):
        dataset = DatasetForTokenClassification([TokenClassificationRecord(text="mock", tokens=["mock"])])
        with pytest.raises(AssertionError):
            dataset.prepare_for_training()

    def test_datasets_empty_metadata(self):
        dataset = DatasetForTokenClassification([TokenClassificationRecord(text="mock", tokens=["mock"])])
        assert dataset.to_datasets()["metadata"] == [None]

    def test_to_from_pandas(self, tokenclassification_records):
        expected_dataset = DatasetForTokenClassification(tokenclassification_records)

        dataset_df = expected_dataset.to_pandas()

        assert isinstance(dataset_df, pd.DataFrame)
        assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

        dataset = DatasetForTokenClassification.from_pandas(dataset_df)

        assert isinstance(dataset, DatasetForTokenClassification)
        for rec, expected in zip(dataset, expected_dataset):
            assert rec == expected

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_push_to_hub(self, tokenclassification_records):
        dataset_ds = DatasetForTokenClassification(tokenclassification_records).to_datasets()
        _push_to_hub_with_retries(
            dataset_ds,
            repo_id="argilla/_test_token_classification_records",
            token=_HF_HUB_ACCESS_TOKEN,
            private=True,
        )
        sleep(1)
        dataset_ds = datasets.load_dataset(
            "argilla/_test_token_classification_records",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )

        assert isinstance(dataset_ds, datasets.Dataset)

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_prepare_for_training_with_spacy(self):
        ner_dataset = datasets.load_dataset(
            "argilla/gutenberg_spacy-ner",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )
        rb_dataset: DatasetForTokenClassification = read_datasets(ner_dataset, task="TokenClassification")
        for r in rb_dataset:
            r.annotation = [(label, start, end) for label, start, end, _ in r.prediction]

        with pytest.raises(ValueError):
            train = rb_dataset.prepare_for_training(framework="spacy", seed=42)

        train = rb_dataset.prepare_for_training(framework="spacy", lang=spacy.blank("en"), seed=42)
        assert isinstance(train, spacy.tokens.DocBin)
        assert len(train) == 100

        nlp = spacy.blank("en")
        train, test = rb_dataset.prepare_for_training(framework="spacy", lang=nlp, train_size=0.8, seed=42)
        assert isinstance(train, spacy.tokens.DocBin)
        assert isinstance(test, spacy.tokens.DocBin)
        assert len(train) == 80
        assert len(test) == 20

        train_doc = next(train.get_docs(nlp.vocab))
        test_doc = next(test.get_docs(nlp.vocab))

        assert "id" in train_doc.user_data
        assert "id" in test_doc.user_data

    def test_prepare_for_training_with_openai(self):
        ner_dataset = datasets.load_dataset(
            # TODO(@frascuchon): Move dataset to the new org
            "rubrix/gutenberg_spacy-ner",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )
        ds: DatasetForTokenClassification = read_datasets(ner_dataset, task="TokenClassification")
        for r in ds:
            r.annotation = [(label, start, end) for label, start, end, _ in r.prediction]
        jsonl = ds.prepare_for_training(framework="openai", seed=42)

        assert isinstance(jsonl, list)
        assert isinstance(jsonl[0], dict)
        assert "prompt" in jsonl[0] and "completion" in jsonl[0] and "id" in jsonl[0]

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_prepare_for_training_with_spark_nlp(self):
        ner_dataset = datasets.load_dataset(
            "argilla/gutenberg_spacy-ner",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )
        rb_dataset: DatasetForTokenClassification = read_datasets(ner_dataset, task="TokenClassification")
        for r in rb_dataset:
            r.annotation = [(label, start, end) for label, start, end, _ in r.prediction]

        train = rb_dataset.prepare_for_training(framework="spark-nlp", seed=42)
        assert isinstance(train, pd.DataFrame)
        assert len(train) == 100

        train, test = rb_dataset.prepare_for_training(framework="spark-nlp", train_size=0.8, seed=42)
        assert isinstance(train, pd.DataFrame)
        assert isinstance(test, pd.DataFrame)
        assert len(train) == 80
        assert len(test) == 20

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_prepare_for_training(self):
        ner_dataset = datasets.load_dataset(
            "argilla/gutenberg_spacy-ner",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )
        rb_dataset: DatasetForTokenClassification = read_datasets(ner_dataset, task="TokenClassification")
        for r in rb_dataset:
            r.annotation = [(label, start, end) for label, start, end, _ in r.prediction]

        train = rb_dataset.prepare_for_training()
        assert (set(train.column_names)) == set(["id", "tokens", "ner_tags"])

        assert isinstance(train, datasets.Dataset) or isinstance(train, datasets.Dataset)
        assert "ner_tags" in train.column_names
        assert len(train) == 100

        assert train.features["ner_tags"].feature == datasets.ClassLabel(
            names=[
                "O",
                "B-CARDINAL",
                "I-CARDINAL",
                "B-DATE",
                "I-DATE",
                "B-FAC",
                "I-FAC",
                "B-GPE",
                "I-GPE",
                "B-LANGUAGE",
                "I-LANGUAGE",
                "B-LOC",
                "I-LOC",
                "B-NORP",
                "I-NORP",
                "B-ORDINAL",
                "I-ORDINAL",
                "B-ORG",
                "I-ORG",
                "B-PERSON",
                "I-PERSON",
                "B-PRODUCT",
                "I-PRODUCT",
                "B-QUANTITY",
                "I-QUANTITY",
                "B-TIME",
                "I-TIME",
                "B-WORK_OF_ART",
                "I-WORK_OF_ART",
            ]
        )

        _push_to_hub_with_retries(
            train,
            repo_id="argilla/_test_token_classification_training",
            token=_HF_HUB_ACCESS_TOKEN,
            private=True,
        )

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_from_dataset_with_non_argilla_format(self):
        ds = datasets.load_dataset(
            "argilla/_wikiann_es_test_100",
            split="test",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
        )

        rb_ds = DatasetForTokenClassification.from_datasets(ds, tags="ner_tags", metadata=["spans"])

        again_the_ds = rb_ds.to_datasets()
        assert again_the_ds.column_names == [
            "text",
            "tokens",
            "prediction",
            "prediction_agent",
            "annotation",
            "annotation_agent",
            "vectors",
            "id",
            "metadata",
            "status",
            "event_timestamp",
            "metrics",
        ]

    def test_from_datasets_with_empty_tokens(self):
        dataset_ds = datasets.Dataset.from_dict({"empty_tokens": [["mock"], []]})

        with pytest.warns(UserWarning, match="Ignoring row with no tokens."):
            dataset_rb = DatasetForTokenClassification.from_datasets(dataset_ds, tokens="empty_tokens")
            assert len(dataset_rb) == 1
            assert dataset_rb[0].tokens == ["mock"]


class TestDatasetForText2Text:
    def test_init(self, text2text_records):
        ds = DatasetForText2Text(text2text_records)
        assert ds._RECORD_TYPE == Text2TextRecord
        assert ds._records == text2text_records

    def test_to_from_datasets(self, text2text_records):
        expected_dataset = DatasetForText2Text(text2text_records)

        dataset_ds = expected_dataset.to_datasets()

        assert isinstance(dataset_ds, datasets.Dataset)
        assert dataset_ds.column_names == [
            "text",
            "prediction",
            "prediction_agent",
            "annotation",
            "annotation_agent",
            "vectors",
            "id",
            "metadata",
            "status",
            "event_timestamp",
            "metrics",
        ]
        assert dataset_ds.features["prediction"] == [
            {
                "text": datasets.Value("string"),
                "score": datasets.Value("float64"),
            }
        ]

        dataset = DatasetForText2Text.from_datasets(dataset_ds)

        assert isinstance(dataset, DatasetForText2Text)
        _compare_datasets(dataset, expected_dataset)

        missing_optional_cols = datasets.Dataset.from_dict({"text": ["mock"]})
        rec = DatasetForText2Text.from_datasets(missing_optional_cols)[0]
        assert rec.text == "mock"

        # alternative format for the predictions
        ds = datasets.Dataset.from_dict({"text": ["example"], "prediction": [["ejemplo"]]})
        rec = DatasetForText2Text.from_datasets(ds)[0]
        assert rec.prediction[0][0] == "ejemplo"
        assert rec.prediction[0][1] == pytest.approx(1.0)

    def test_from_to_datasets_id(self):
        record = Text2TextRecord(text="mock")
        dataset_rb = DatasetForText2Text([record])
        dataset_ds = dataset_rb.to_datasets()
        assert dataset_ds["id"] == [record.id]

        assert read_datasets(dataset_ds, task="Text2Text")[0].id == record.id

    def test_datasets_empty_metadata(self):
        dataset = DatasetForText2Text([Text2TextRecord(text="mock")])
        assert dataset.to_datasets()["metadata"] == [None]

    def test_to_from_pandas(self, text2text_records):
        expected_dataset = DatasetForText2Text(text2text_records)

        dataset_df = expected_dataset.to_pandas()

        assert isinstance(dataset_df, pd.DataFrame)
        assert list(dataset_df.columns) == list(expected_dataset[0].__fields__.keys())

        dataset = DatasetForText2Text.from_pandas(dataset_df)

        assert isinstance(dataset, DatasetForText2Text)
        for rec, expected in zip(dataset, expected_dataset):
            assert rec == expected

    def test_prepare_for_training(self):
        ds = DatasetForText2Text([Text2TextRecord(text="mock", annotation="mock"), Text2TextRecord(text="mock")] * 10)
        train = ds.prepare_for_training(train_size=1, seed=42)

        assert isinstance(train, datasets.Dataset)
        assert set(train.column_names) == set(["id", "text", "target"])
        assert len(train) == 10
        assert train[1]["text"] == "mock"
        assert train[1]["target"] == "mock"
        assert train.features["text"] == datasets.Value("string")
        assert train.features["target"] == datasets.Value("string")

        train_test = ds.prepare_for_training(train_size=0.5, seed=42)
        assert len(train_test["train"]) == 5
        assert len(train_test["test"]) == 5
        for split in ["train", "test"]:
            assert set(train_test[split].column_names) == set(["id", "text", "target"])

    def test_prepare_for_training_with_spacy(self):
        ds = DatasetForText2Text([Text2TextRecord(text="mock", annotation="mock"), Text2TextRecord(text="mock")] * 10)
        with pytest.raises(NotImplementedError):
            ds.prepare_for_training("spacy", lang=spacy.blank("en"), train_size=1)

    def test_prepare_for_training_with_openai(self):
        ds = DatasetForText2Text(
            [Text2TextRecord(text="Michael is a professor at Harvard but", annotation=" he used to work at MIT")]
        )

        jsonl = ds.prepare_for_training(framework="openai", seed=42)

        assert isinstance(jsonl, list)
        assert isinstance(jsonl[0], dict)
        assert "prompt" in jsonl[0] and "completion" in jsonl[0] and "id" in jsonl[0]
        assert jsonl[0]["prompt"] == "Michael is a professor at Harvard but\n\n###\n\n"

    def test_prepare_for_training_with_spark_nlp(self):
        ds = DatasetForText2Text([Text2TextRecord(text="mock", annotation="mock"), Text2TextRecord(text="mock")] * 10)
        df = ds.prepare_for_training("spark-nlp", train_size=1)
        assert list(df.columns) == ["id", "text", "target"]

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_push_to_hub(self, text2text_records):
        dataset_ds = DatasetForText2Text(text2text_records).to_datasets()
        _push_to_hub_with_retries(
            dataset_ds,
            repo_id="argilla/_test_text2text_records",
            token=_HF_HUB_ACCESS_TOKEN,
            private=True,
        )
        sleep(1)
        dataset_ds = datasets.load_dataset(
            "argilla/_test_text2text_records",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
            split="train",
        )

        assert isinstance(dataset_ds, datasets.Dataset)

    @pytest.mark.skipif(
        _HF_HUB_ACCESS_TOKEN is None,
        reason="You need a HF Hub access token to test the push_to_hub feature",
    )
    def test_from_dataset_with_non_argilla_format(self):
        ds = datasets.load_dataset(
            "argilla/_big_patent_a_test_100",
            split="test",
            use_auth_token=_HF_HUB_ACCESS_TOKEN,
        )

        rb_ds = DatasetForText2Text.from_datasets(ds, text="description", annotation="abstract")

        again_the_ds = rb_ds.to_datasets()
        assert again_the_ds.column_names == [
            "text",
            "prediction",
            "prediction_agent",
            "annotation",
            "annotation_agent",
            "vectors",
            "id",
            "metadata",
            "status",
            "event_timestamp",
            "metrics",
        ]


def _compare_datasets(dataset, expected_dataset):
    for rec, expected in zip(dataset, expected_dataset):
        for col in expected.__fields__.keys():
            # TODO: have to think about how we deal with `None`s
            if col in ["metadata", "metrics"]:
                continue
            assert getattr(rec, col) == getattr(expected, col), f"Wrong column value '{col}'"


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

    monkeypatch.setattr(f"argilla_v1.client.datasets.{dataset_class}.from_pandas", mock_from_pandas)

    assert read_pandas("mock", task) == "mock"


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

    monkeypatch.setattr(f"argilla_v1.client.datasets.{dataset_class}.from_datasets", mock_from_datasets)

    assert read_datasets("mock", task) == "mock"
