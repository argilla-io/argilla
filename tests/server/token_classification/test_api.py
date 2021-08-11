from fastapi.testclient import TestClient
from rubrix.server.server import app
from rubrix.server.tasks.commons import BulkResponse
from rubrix.server.tasks.token_classification import (
    TokenClassificationQuery,
    TokenClassificationSearchRequest,
    TokenClassificationSearchResults,
)
from rubrix.server.tasks.token_classification.api import (
    TokenClassificationBulkData,
    TokenClassificationRecord,
)

client = TestClient(app)


def test_search_special_characters():
    dataset = "test_search_special_characters"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200
    expected_text = "This is a text with !"
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": expected_text.split(" "),
                "raw_text": expected_text,
            }
        ]
    ]
    client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkData(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    response = client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json=TokenClassificationSearchRequest(
            query=TokenClassificationQuery(query_text="\!")
        ).dict(),
    )
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1



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


def test_multiple_mentions_in_same_record():
    dataset = "test_multiple_mentions_in_same_record"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200
    entity_a, entity_b = ("TESTA", "TESTB")

    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "prediction": {
                    "agent": "test",
                    "entities": [
                        {"start": 0, "end": 4, "label": entity_a},
                        {"start": 5, "end": 7, "label": entity_b},
                    ],
                },
            },
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "prediction": {
                    "agent": "test",
                    "entities": [{"start": 0, "end": 4, "label": entity_a}],
                },
            },
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "annotation": {
                    "agent": "test",
                    "entities": [{"start": 0, "end": 4, "label": entity_a}],
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
    assert bulk_response.processed == 3

    response = client.post(f"/api/datasets/{dataset}/TokenClassification:search")
    assert response.status_code == 200, response.json()
    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert "This" in results.aggregations.predicted_mentions[entity_a]
    assert results.aggregations.predicted_mentions[entity_a]["This"] == 2
    assert "is" in results.aggregations.predicted_mentions[entity_b]
    assert results.aggregations.predicted_mentions[entity_b]["is"] == 1
