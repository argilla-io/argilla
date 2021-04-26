import os

import pandas
from fastapi.testclient import TestClient
from rubrix.server.server import app
from rubrix.server.snapshots.model import DatasetSnapshot
from rubrix.server.tasks.commons import TaskStatus
from rubrix.server.tasks.text_classification.api import (
    TaskType,
    TextClassificationBulkData,
    TextClassificationRecord,
)

client = TestClient(app)


def create_some_data_for_text_classification(name: str, n: int):
    records = [
        TextClassificationRecord(**data)
        for idx in range(0, n or 10, 2)
        for data in [
            {
                "id": idx,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "status": TaskStatus.validated,
                "annotation": {
                    "agent": "test",
                    "labels": [
                        {"class": "Test"},
                        {"class": "Mocking"},
                    ],
                },
            },
            {
                "id": idx + 1,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "another value one", "field_two": "value 2"},
                "status": TaskStatus.validated,
                "prediction": {
                    "agent": "test",
                    "labels": [
                        {"class": "NoClass"},
                    ],
                },
                "annotation": {
                    "agent": "test",
                    "labels": [
                        {"class": "Test"},
                    ],
                },
            },
        ]
    ]
    client.post(
        f"/api/datasets/{name}/{TaskType.text_classification}:bulk",
        json=TextClassificationBulkData(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )


def uri_2_path(uri: str):
    from urllib.parse import urlparse

    p = urlparse(uri)
    return os.path.abspath(os.path.join(p.netloc, p.path))


def test_dataset_snapshots_flow():
    name = "test_create_dataset_snapshot"
    api_ds_prefix = f"/api/datasets/{name}"
    # Clear eventually already created snapshots
    response = client.get(f"{api_ds_prefix}/snapshots")
    if response.status_code == 200:
        for snapshot in map(DatasetSnapshot.parse_obj, response.json()):
            assert (
                200
                == client.delete(f"{api_ds_prefix}/snapshots/{snapshot.id}").status_code
            )

    assert client.delete(api_ds_prefix).status_code == 200
    expected_data = 2
    create_some_data_for_text_classification(name, n=expected_data)
    response = client.post(f"{api_ds_prefix}/snapshots")
    assert response.status_code == 200

    snapshot = DatasetSnapshot(**response.json())
    assert snapshot.task == TaskType.text_classification
    assert snapshot.creation_date

    response = client.get(f"{api_ds_prefix}/snapshots")
    assert response.status_code == 200
    snapshots = list(map(DatasetSnapshot.parse_obj, response.json()))
    assert len(snapshots) == 1
    assert snapshots[0] == snapshot

    response = client.get(f"{api_ds_prefix}/snapshots/{snapshot.id}")
    assert response.status_code == 200
    assert snapshot == DatasetSnapshot(**response.json())

    response = client.get(f"{api_ds_prefix}/snapshots/{snapshot.id}/data")
    df = pandas.read_json(response.content, lines=True)
    assert len(df) == expected_data

    client.delete(f"{api_ds_prefix}/snapshots/{snapshot.id}")
    response = client.get(f"{api_ds_prefix}/snapshots/{snapshot.id}")
    assert response.status_code == 404
