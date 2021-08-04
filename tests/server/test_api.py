import os

from fastapi.testclient import TestClient
from rubrix.server.server import app
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

