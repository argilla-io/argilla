import datetime
from time import sleep
from typing import Iterable

import httpx
import pandas
import pytest
import requests
import rubrix
from fastapi.testclient import TestClient
from rubrix import (
    RubrixClient,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
)
from rubrix.sdk.models import DatasetSnapshot, TextClassificationSearchResults
from rubrix.server.server import app
from rubrix.server.tasks.commons import TaskType

from tests.server.snapshots.test_api import create_some_data_for_text_classification

client = TestClient(app)


def mocking_client(monkeypatch):
    monkeypatch.setattr(requests, "get", client.get)
    monkeypatch.setattr(requests, "post", client.post)
    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "delete", client.delete)

    def stream_mock(*args, url: str, **kwargs):
        if "POST" in args:
            return client.post(url, stream=True, **kwargs)
        return client.get(url, stream=True, **kwargs)

    monkeypatch.setattr(httpx, "stream", stream_mock)


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


def test_snapshots(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_create_dataset_snapshot"
    client.delete(f"/api/datasets/{dataset}")
    sleep(1)
    api_ds_prefix = f"/api/datasets/{dataset}"

    expected_data = 100
    create_some_data_for_text_classification(dataset, n=expected_data)
    response = client.post(f"{api_ds_prefix}/snapshots")
    assert response.status_code == 200
    snapshots = rubrix.snapshots(dataset)
    assert len(snapshots) > 0
    for snapshot in snapshots:
        assert snapshot.task == TaskType.text_classification
        assert snapshot.id
        assert snapshot.creation_date

    ds = rubrix.load(name=dataset)
    assert isinstance(ds, pandas.DataFrame)
    assert len(ds) == expected_data
    records = list(
        map(lambda r: TextClassificationRecord(**r), ds.to_dict(orient="records"))
    )

    ds = rubrix.load(name=dataset, snapshot=snapshots[0].id)
    assert isinstance(ds, pandas.DataFrame)


def test_load_limits(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_load_limits"
    api_ds_prefix = f"/api/datasets/{dataset}"
    client.delete(api_ds_prefix)

    create_some_data_for_text_classification(dataset, 50)
    response = client.post(f"{api_ds_prefix}/snapshots")

    limit_data_to = 10
    ds = rubrix.load(name=dataset, limit=limit_data_to)
    assert isinstance(ds, pandas.DataFrame)
    assert len(ds) == limit_data_to

    snapshot = rubrix.snapshots(dataset)[0]
    ds = rubrix.load(name=dataset, snapshot=snapshot.id, limit=limit_data_to)
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
        rubrix.snapshots(name="not_found")

    with pytest.raises(Exception, match=not_found_match):
        rubrix.load(name="not-found")

    with pytest.raises(Exception, match=not_found_match):
        rubrix.load(name="not-found", snapshot="blabla")


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


@pytest.mark.parametrize("annotation", ["gold_label", ["multi_label1", "multi_label2"]])
def test_text_classification_record_to_sdk(annotation):
    token_attributions = [
        TokenAttributions(token="test", attributions={"label1": 1.0, "label2": 2.0})
    ]
    record = TextClassificationRecord(
        inputs={"text": "test"},
        prediction=[("label1", 0.5), ("label2", 0.5)],
        annotation=annotation,
        prediction_agent="test_model",
        annotation_agent="test_annotator",
        multi_label=True,
        explanation={"text": token_attributions},
        id=1,
        metadata={"metadata": "test"},
        status="Default",
        event_timestamp=datetime.datetime(2000, 1, 1),
    )
    sdk_record = RubrixClient._text_classification_record_to_sdk(record)

    assert sdk_record.event_timestamp == datetime.datetime(2000, 1, 1)


def test_token_classification_record_to_sdk():
    record = TokenClassificationRecord(
        text="test text",
        tokens=["test", "text"],
        prediction=[("label", 0, 5)],
        annotation=[("label", 0, 5)],
        prediction_agent="test_model",
        annotation_agent="test_annotator",
        id=1,
        metadata={"metadata": "test"},
        status="Default",
        event_timestamp=datetime.datetime(2000, 1, 1),
    )
    sdk_record = RubrixClient._token_classification_record_to_sdk(record)

    assert sdk_record.event_timestamp == datetime.datetime(2000, 1, 1)


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
    api_ds_prefix = f"/api/datasets/{dataset}"

    expected_data = 100
    create_some_data_for_text_classification(dataset, n=expected_data)
    response = client.post(f"{api_ds_prefix}/snapshots")
    assert response.status_code == 200
    snapshot = DatasetSnapshot.from_dict(response.json())
    ds = rubrix.load(name=dataset, ids=[3, 5])
    assert len(ds) == 2

    ds = rubrix.load(name=dataset, ids=[3, 5], snapshot=snapshot.id)
    assert len(ds) == 100


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
