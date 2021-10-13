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

import datetime
import socket
from time import sleep
from typing import Iterable

import httpx
import pandas
import pytest

import rubrix
from rubrix import (
    RubrixClient,
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from rubrix.sdk.models import TextClassificationSearchResults
from tests.server.test_api import create_some_data_for_text_classification
from tests.server.test_helpers import client


def mocking_client(monkeypatch):
    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "delete", client.delete)
    monkeypatch.setattr(httpx, "put", client.put)
    monkeypatch.setattr(httpx, "stream", client.stream)


def test_log_something(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test-dataset"
    client.delete(f"/api/datasets/{dataset_name}")

    response = rubrix.log(
        name=dataset_name,
        records=rubrix.TextClassificationRecord(inputs={"text": "This is a test"}),
    )

    assert response.processed == 1
    assert response.failed == 0

    response = client.post(f"/api/datasets/{dataset_name}/TextClassification:search")
    results = TextClassificationSearchResults.from_dict(response.json())
    assert results.total == 1
    assert len(results.records) == 1
    assert results.records[0].inputs["text"] == "This is a test"


def test_load_limits(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_load_limits"
    api_ds_prefix = f"/api/datasets/{dataset}"
    client.delete(api_ds_prefix)

    create_some_data_for_text_classification(dataset, 50)

    limit_data_to = 10
    ds = rubrix.load(name=dataset, limit=limit_data_to)
    assert isinstance(ds, pandas.DataFrame)
    assert len(ds) == limit_data_to

    ds = rubrix.load(name=dataset, limit=limit_data_to)
    assert isinstance(ds, pandas.DataFrame)
    assert len(ds) == limit_data_to


def test_log_records_with_too_long_text(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test_log_records_with_too_long_text"
    client.delete(f"/api/datasets/{dataset_name}")
    item = TextClassificationRecord(
        inputs={"text": "This is a toooooo long text\n" * 10000}
    )

    rubrix.log([item], name=dataset_name)


def test_not_found_response(monkeypatch):
    mocking_client(monkeypatch)
    not_found_match = "Not found error. The API answered with a 404 code"

    with pytest.raises(Exception, match=not_found_match):
        rubrix.load(name="not-found")


def test_single_record(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test_log_single_records"
    client.delete(f"/api/datasets/{dataset_name}")
    item = TextClassificationRecord(
        inputs={"text": "This is a single record. Only this. No more."}
    )

    rubrix.log(item, name=dataset_name)


def test_passing_wrong_iterable_data(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test_log_single_records"
    client.delete(f"/api/datasets/{dataset_name}")
    with pytest.raises(Exception, match="Unknown record type passed"):
        rubrix.log({"a": "010", "b": 100}, name=dataset_name)


def test_log_with_generator(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test_log_with_generator"
    client.delete(f"/api/datasets/{dataset_name}")

    def generator(items: int = 10) -> Iterable[TextClassificationRecord]:
        for i in range(0, items):
            yield TextClassificationRecord(id=i, inputs={"text": "The text data"})

    rubrix.log(generator(), name=dataset_name)


def test_log_with_annotation(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test_log_with_annotation"
    client.delete(f"/api/datasets/{dataset_name}")
    rubrix.log(
        TextClassificationRecord(
            id=0,
            inputs={"text": "The text data"},
            annotation="T",
            annotation_agent="test",
        ),
        name=dataset_name,
    )

    df = rubrix.load(dataset_name)
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["status"] == "Validated"

    rubrix.log(
        TextClassificationRecord(
            id=0,
            inputs={"text": "The text data"},
            annotation="T",
            annotation_agent="test",
            status="Discarded",
        ),
        name=dataset_name,
    )
    df = rubrix.load(dataset_name)
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["status"] == "Discarded"


def test_create_ds_with_wrong_name(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "Test Create_ds_with_wrong_name"
    client.delete(f"/api/datasets/{dataset_name}")

    with pytest.raises(
        Exception,
        match="msg='string does not match regex",
    ):
        rubrix.log(
            TextClassificationRecord(
                inputs={"text": "The text data"},
            ),
            name=dataset_name,
        )


def test_delete_dataset(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test_delete_dataset"
    client.delete(f"/api/datasets/{dataset_name}")

    rubrix.log(
        TextClassificationRecord(
            id=0,
            inputs={"text": "The text data"},
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset_name,
    )
    rubrix.load(name=dataset_name)
    rubrix.delete(name=dataset_name)
    sleep(1)
    with pytest.raises(
        Exception, match="Not found error. The API answered with a 404 code"
    ):
        rubrix.load(name=dataset_name)


def test_dataset_copy(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_dataset_copy"
    dataset_copy = "new_dataset"

    client.delete(f"/api/datasets/{dataset}")
    client.delete(f"/api/datasets/{dataset_copy}")

    rubrix.log(
        TextClassificationRecord(
            id=0,
            inputs="This is the record input",
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )
    rubrix.copy(dataset, name_of_copy=dataset_copy)
    df = rubrix.load(name=dataset)
    df_copy = rubrix.load(name=dataset_copy)

    assert df.equals(df_copy)

    with pytest.raises(Exception):
        rubrix.copy(dataset, name_of_copy=dataset_copy)


def test_text_classifier_with_inputs_list(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_text_classifier_with_inputs_list"
    client.delete(f"/api/datasets/{dataset}")

    expected_inputs = ["A", "List", "of", "values"]
    rubrix.log(
        TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )

    df = rubrix.load(name=dataset)
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["inputs"]["text"] == expected_inputs


def test_load_with_ids_list(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_load_with_ids_list"
    client.delete(f"/api/datasets/{dataset}")
    sleep(1)

    expected_data = 100
    create_some_data_for_text_classification(dataset, n=expected_data)
    ds = rubrix.load(name=dataset, ids=[3, 5])
    assert len(ds) == 2


def test_token_classification_spans(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_token_classification_with_consecutive_spans"
    texto = "Esto es una prueba"
    item = rubrix.TokenClassificationRecord(
        text=texto,
        tokens=texto.split(),
        prediction=[("test", 1, 2)],  # Inicio y fin son consecutivos
        prediction_agent="test",
    )
    with pytest.raises(
        Exception, match=r"Defined offset \[s\] is a misaligned entity mention"
    ):
        rubrix.log(item, name=dataset)

    item.prediction = [("test", 0, 6)]
    with pytest.raises(
        Exception, match=r"Defined offset \[Esto e\] is a misaligned entity mention"
    ):
        rubrix.log(item, name=dataset)

    item.prediction = [("test", 0, 4)]
    rubrix.log(item, name=dataset)


def test_load_text2text(monkeypatch):
    mocking_client(monkeypatch)
    records = [
        Text2TextRecord(
            text="test text",
            prediction=["test prediction"],
            annotation="test annotation",
            prediction_agent="test_model",
            annotation_agent="test_annotator",
            id=str(i),
            metadata={"metadata": "test"},
            status="Default",
            event_timestamp=datetime.datetime(2000, 1, 1),
        )
        for i in range(0, 100)
    ]

    rubrix.log(records, name="test_load_text2text")
    df = rubrix.load(name="test_load_text2text")
    assert len(df) == 100
