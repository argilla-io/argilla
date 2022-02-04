from rubrix.client.sdk.text2text.models import Text2TextBulkData
from rubrix.server.tasks.commons import BulkResponse
from rubrix.server.tasks.text2text import (
    CreationText2TextRecord,
    Text2TextSearchResults,
)
from tests.server.test_helpers import client


def test_search_records():
    dataset = "test_search_records"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    records = [
        CreationText2TextRecord.parse_obj(data)
        for data in [
            {
                "id": 0,
                "text": "This is a text data",
                "metadata": {
                    "field_one": "value one",
                },
                "prediction": {
                    "agent": "test",
                    "sentences": [{"text": "This is a test data", "score": 0.6}],
                },
            },
            {
                "id": 1,
                "text": "Ånother data",
            },
        ]
    ]
    response = client.post(
        f"/api/datasets/{dataset}/Text2Text:bulk",
        json=Text2TextBulkData(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 2

    response = client.post(f"/api/datasets/{dataset}/Text2Text:search", json={})
    assert response.status_code == 200, response.json()
    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == 2
    assert results.records[0].predicted is None

    assert results.aggregations.dict() == {
        "annotated_as": {},
        "annotated_by": {},
        "annotated_text": {},
        "metadata": {"field_one": {"value one": 1}},
        "predicted": {},
        "predicted_as": {},
        "predicted_by": {"test": 1},
        "predicted_text": {},
        "score": {
            "0.0-0.05": 0,
            "0.05-0.1": 0,
            "0.1-0.15": 0,
            "0.15-0.2": 0,
            "0.2-0.25": 0,
            "0.25-0.3": 0,
            "0.3-0.35": 0,
            "0.35-0.4": 0,
            "0.4-0.45": 0,
            "0.45-0.5": 0,
            "0.5-0.55": 0,
            "0.55-0.6": 0,
            "0.6-0.65": 1,
            "0.65-0.7": 0,
            "0.7-0.75": 0,
            "0.75-0.8": 0,
            "0.8-0.85": 0,
            "0.85-0.9": 0,
            "0.9-0.95": 0,
            "0.95-1.0": 0,
            "1.0-*": 0,
        },
        "status": {"Default": 2},
        "words": {"data": 2, "ånother": 1},
    }
