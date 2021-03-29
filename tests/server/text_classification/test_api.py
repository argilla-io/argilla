from datetime import datetime
from time import sleep

from fastapi.testclient import TestClient
from rubrix.server.commons.models import PredictionStatus, SortParam
from rubrix.server.datasets.model import Dataset
from rubrix.server.server import app
from rubrix.server.text_classification.api import (
    BulkResponse,
    TextClassificationSearchResults,
    TextClassificationRecordsBulk,
)
from rubrix.server.text_classification.model import (
    TextClassificationAggregations,
    TextClassificationAnnotation,
    TextClassificationQuery,
    TextClassificationRecord,
)
from rubrix.server.token_classification.api import TokenClassificationRecordsBulk
from rubrix.server.token_classification.model import TokenClassificationRecord

client = TestClient(app)


def test_records_with_default_text():
    dataset = "test_records_with_default_text"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [{"tokens": "This is a text".split(" ")}]
    ]
    response = client.post(
        "/api/token-classification/datasets/:bulk-records",
        json=TokenClassificationRecordsBulk(
            name=dataset,
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    sleep(1)

    response = client.post(f"/api/classification/datasets/{dataset}/:search", json={})

    assert response.status_code == 200
    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    assert results.records[0].text == {"text": "This is a text"}


def test_create_records_for_text_classification_with_multi_label():
    dataset = "test_create_records_for_text_classification_with_multi_label"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    records = [
        TextClassificationRecord.parse_obj(data)
        for data in [
            {
                "id": 0,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "prediction": {
                    "agent": "test",
                    "labels": [
                        {"class": "Test", "confidence": 0.6},
                        {"class": "Mocking", "confidence": 0.7},
                        {"class": "NoClass", "confidence": 0.2},
                    ],
                },
            },
            {
                "id": 1,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "another value one", "field_two": "value 2"},
                "prediction": {
                    "agent": "test",
                    "labels": [
                        {"class": "Test", "confidence": 0.6},
                        {"class": "Mocking", "confidence": 0.7},
                        {"class": "NoClass", "confidence": 0.2},
                    ],
                },
            },
        ]
    ]
    response = client.post(
        "/api/classification/datasets/:bulk-records",
        json=TextClassificationRecordsBulk(
            name=dataset,
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

    response = client.post(
        "/api/classification/datasets/:bulk-records",
        json=TextClassificationRecordsBulk(
            name=dataset,
            tags={"new": "tag"},
            metadata={"new": {"metadata": "value"}},
            records=records,
        ).dict(by_alias=True),
    )

    get_dataset = Dataset.parse_obj(
        client.get(f"/api/datasets/{dataset}").json()
    )
    assert get_dataset.tags == {
        "env": "test",
        "class": "text classification",
        "new": "tag",
    }
    assert get_dataset.metadata == {
        "config": {"the": "config"},
        "new": {"metadata": "value"},
    }

    assert response.status_code == 200, response.json()

    sleep(1)
    response = client.post(f"/api/classification/datasets/{dataset}/:search", json={})

    assert response.status_code == 200
    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 2
    assert results.aggregations.predicted_as == {"Mocking": 2, "Test": 2}
    assert results.records[0].predicted is None


def test_create_records_for_text_classification():
    dataset = "test_create_records_for_text_classification"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200
    tags = {"env": "test", "class": "text classification"}
    metadata = {"config": {"the": "config"}}
    classification_bulk = TextClassificationRecordsBulk(
        name=dataset,
        tags=tags,
        metadata=metadata,
        records=[
            TextClassificationRecord(
                **{
                    "id": 0,
                    "inputs": {"data": "my data"},
                    "prediction": {
                        "agent": "test",
                        "labels": [
                            {"class": "Test", "confidence": 0.3},
                            {"class": "Mocking", "confidence": 0.7},
                        ],
                    },
                }
            )
        ],
    )
    response = client.post(
        "/api/classification/datasets/:bulk-records",
        json=classification_bulk.dict(by_alias=True),
    )

    assert response.status_code == 200
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 1

    response = client.get(f"/api/datasets/{dataset}")
    assert response.status_code == 200
    created_dataset = Dataset.parse_obj(response.json())
    assert created_dataset.tags == tags
    assert created_dataset.metadata == metadata

    sleep(1)
    response = client.post(f"/api/classification/datasets/{dataset}/:search", json={})

    assert response.status_code == 200
    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    assert results.aggregations.predicted_as == {"Mocking": 1}
    assert results.aggregations.status == {"Default": 1}
    assert results.aggregations.confidence
    assert results.aggregations.predicted == {}


def test_partial_record_update():
    name = "test_partial_record_update"
    assert client.delete(f"/api/datasets/{name}").status_code == 200

    record = TextClassificationRecord(
        **{
            "id": 1,
            "inputs": {"text": "This is a text, oh yeah!"},
            "prediction": {
                "agent": "test",
                "labels": [
                    {"class": "Positive", "confidence": 0.6},
                    {"class": "Negative", "confidence": 0.3},
                    {"class": "Other", "confidence": 0.1},
                ],
            },
        }
    )

    bulk = TextClassificationRecordsBulk(
        name=name,
        records=[record],
    )

    response = client.post(
        "/api/classification/datasets/:bulk-records",
        json=bulk.dict(by_alias=True),
    )

    assert response.status_code == 200
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.failed == 0
    assert bulk_response.processed == 1

    record.annotation = TextClassificationAnnotation.parse_obj(
        {
            "agent": "gold_standard",
            "labels": [{"class": "Positive"}],
        }
    )

    bulk.records = [record]
    sleep(1)

    client.post(
        "/api/classification/datasets/:bulk-records",
        json=bulk.dict(by_alias=True),
    )

    sleep(1)
    response = client.post(
        f"/api/classification/datasets/{name}/:search",
        json={
            "query": TextClassificationQuery(predicted=PredictionStatus.OK).dict(
                by_alias=True
            ),
            "sort": [SortParam(by="annotated_as").dict(by_alias=True)],
        },
    )

    assert response.status_code == 200
    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    first_record = results.records[0]
    assert TextClassificationRecord(
        **first_record.dict(by_alias=True, exclude_none=True)
    ) == TextClassificationRecord(
        **{
            "id": 1,
            "inputs": {"text": "This is a text, oh yeah!"},
            "prediction": {
                "agent": "test",
                "labels": [
                    {"class": "Positive", "confidence": 0.6},
                    {"class": "Negative", "confidence": 0.3},
                    {"class": "Other", "confidence": 0.1},
                ],
            },
            "annotation": {
                "agent": "gold_standard",
                "labels": [{"class": "Positive"}],
            },
        }
    )


def test_sort_by_id_as_default():
    dataset = "test_sort_by_id_as_default"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200
    response = client.post(
        "/api/classification/datasets/:bulk-records",
        json=TextClassificationRecordsBulk(
            name=dataset,
            records=[
                TextClassificationRecord(
                    **{
                        "id": i,
                        "inputs": {"data": "my data"},
                        "metadata": {"s": "value"},
                    }
                )
                for i in range(0, 100)
            ],
        ).dict(by_alias=True),
    )
    sleep(1)
    response = client.post(
        f"/api/classification/datasets/{dataset}/:search?from=0&limit=10",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert list(map(lambda r: r.id, results.records)) == [
        0,
        1,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
    ]


def test_disable_aggregations_when_scroll():
    dataset = "test_disable_aggregations_when_scroll"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        "/api/classification/datasets/:bulk-records",
        json=TextClassificationRecordsBulk(
            name=dataset,
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=[
                TextClassificationRecord(
                    **{
                        "id": i,
                        "inputs": {"data": "my data"},
                        "prediction": {
                            "agent": "test",
                            "labels": [
                                {"class": "Test", "confidence": 0.3},
                                {"class": "Mocking", "confidence": 0.7},
                            ],
                        },
                    }
                )
                for i in range(0, 100)
            ],
        ).dict(by_alias=True),
    )
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.processed == 100

    sleep(1)
    response = client.post(
        f"/api/classification/datasets/{dataset}/:search?from=10",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert results.aggregations == TextClassificationAggregations()


def test_include_event_timestamp():
    dataset = "test_include_event_timestamp"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        "/api/classification/datasets/:bulk-records",
        data=TextClassificationRecordsBulk(
            name=dataset,
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=[
                TextClassificationRecord(
                    **{
                        "id": i,
                        "inputs": {"data": "my data"},
                        "event_timestamp": datetime.utcnow(),
                        "prediction": {
                            "agent": "test",
                            "labels": [
                                {"class": "Test", "confidence": 0.3},
                                {"class": "Mocking", "confidence": 0.7},
                            ],
                        },
                    }
                )
                for i in range(0, 100)
            ],
        ).json(by_alias=True),
    )
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.processed == 100

    sleep(1)
    response = client.post(
        f"/api/classification/datasets/{dataset}/:search?from=10",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert all(map(lambda record: record.event_timestamp is not None, results.records))


def test_words_cloud():
    dataset = "test_language_detection"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        "/api/classification/datasets/:bulk-records",
        data=TextClassificationRecordsBulk(
            name=dataset,
            records=[
                TextClassificationRecord(
                    **{
                        "id": 0,
                        "inputs": {"text": "Esto es un ejemplo de texto"},
                    }
                ),
                TextClassificationRecord(
                    **{
                        "id": 1,
                        "inputs": {"text": "This is an simple text example"},
                    }
                ),
                TextClassificationRecord(
                    **{
                        "id": 2,
                        "inputs": {"text": "C'est nes pas une pipe"},
                    }
                ),
            ],
        ).json(by_alias=True),
    )
    BulkResponse.parse_obj(response.json())

    sleep(1)
    response = client.post(
        f"/api/classification/datasets/{dataset}/:search",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.aggregations.words is not None
