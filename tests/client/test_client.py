from time import sleep

import httpx
import requests
from fastapi.testclient import TestClient
from rubrix.sdk.models import TextClassificationSearchResults
from rubrix.server.commons.models import TaskType
from rubrix.server.server import app

import rubrix

from tests.server.snapshots.test_api import create_some_data_for_text_classification

client = TestClient(app)


def mocking_client(monkeypatch):
    monkeypatch.setattr(requests, "get", client.get)
    monkeypatch.setattr(requests, "post", client.post)
    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "get", client.get)

    def stream_mock(*args, url: str, **kwargs):
        return client.get(url, stream=True)

    monkeypatch.setattr(httpx, "stream", stream_mock)


def test_log_something(monkeypatch):
    mocking_client(monkeypatch)
    dataset_name = "test-dataset"

    client.delete(f"/api/datasets/{dataset_name}")

    response = rubrix.log(
        name=dataset_name,
        records=[rubrix.TextClassificationRecord(inputs={"text": "This is a test"})],
    )

    assert response.processed == 1
    assert response.failed == 0

    sleep(1)

    response = client.post(f"/api/datasets/{dataset_name}/TextClassification/:search")
    results = TextClassificationSearchResults.from_dict(response.json())
    assert results.total == 1
    assert len(results.records) == 1
    assert results.records[0].inputs["text"] == "This is a test"


def test_list_snapshots(monkeypatch):
    mocking_client(monkeypatch)
    dataset = "test_create_dataset_snapshot"
    api_ds_prefix = f"/api/datasets/{dataset}"
    create_some_data_for_text_classification(dataset)
    response = client.post(
        f"{api_ds_prefix}/snapshots?task={TaskType.text_classification}"
    )
    assert response.status_code == 200
    snapshots = rubrix.snapshots(dataset)
    assert len(snapshots) > 0
    for snapshot in snapshots:
        assert snapshot.task == TaskType.text_classification
        assert snapshot.id
        assert snapshot.creation_date

    ds = rubrix.load(name=dataset)
    assert ds

    ds = rubrix.load(name=dataset, snapshot=snapshots[0].id)
    assert ds

