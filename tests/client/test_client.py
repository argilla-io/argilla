from time import sleep

import httpx
import requests
from fastapi.testclient import TestClient
from rubrix import TextClassificationSearchResults
from rubrix.server.server import app

import rubrix

client = TestClient(app)


def test_log_something(monkeypatch):
    monkeypatch.setattr(requests, "get", client.get)
    monkeypatch.setattr(requests, "post", client.post)
    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "get", client.get)

    dataset_name = "test-dataset"

    client.delete(f"/api/datasets/{dataset_name}")

    response = rubrix.log(
        name=dataset_name,
        records=[
            rubrix.TextClassificationRecord.from_dict(
                {"inputs": {"text": "This is a test"}}
            )
        ],
    )

    assert response.processed == 1
    assert response.failed == 0

    sleep(1)

    response = client.post(f"/api/datasets/{dataset_name}/TextClassification/:search")
    results = TextClassificationSearchResults.from_dict(response.json())
    assert results.total == 1
    assert len(results.records) == 1
    assert results.records[0].inputs["text"] == "This is a test"
