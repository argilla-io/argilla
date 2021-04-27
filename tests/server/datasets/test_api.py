import pytest
from fastapi.testclient import TestClient
from rubrix.server.server import app
from rubrix.server.tasks.text_classification import TextClassificationBulkData

client = TestClient(app)


def test_dataset_naming_validation():
    request = TextClassificationBulkData(records=[])
    dataset = "Wrong dataset name"

    assert (
        client.post(
            f"/api/datasets/{dataset}/TextClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 422
    )

    assert (
        client.post(
            f"/api/datasets/{dataset}/TokenClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 422
    )
