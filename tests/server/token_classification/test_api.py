from fastapi.testclient import TestClient
from rubrix.server.server import app
from rubrix.server.tasks.commons import BulkResponse
from rubrix.server.tasks.token_classification import TokenClassificationSearchResults
from rubrix.server.tasks.token_classification.api import (
    TokenClassificationBulkData,
    TokenClassificationRecord,
)

client = TestClient(app)


def test_create_records_for_token_classification():
    dataset = "test_create_records_for_token_classification"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200
    entity_label = "TEST"

    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "prediction": {
                    "agent": "test",
                    "entities": [{"start": 0, "end": 4, "label": entity_label}],
                },
            },
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "annotation": {
                    "agent": "test",
                    "entities": [{"start": 0, "end": 4, "label": entity_label}],
                },
            },
        ]
    ]
    response = client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkData(
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

    response = client.post(f"/api/datasets/{dataset}/TokenClassification:search")
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert "This" in results.aggregations.predicted_mentions[entity_label]
    assert "This" in results.aggregations.mentions[entity_label]
