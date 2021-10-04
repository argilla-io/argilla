#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from datetime import datetime

import pytest

from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons import BulkResponse, PredictionStatus
from rubrix.server.tasks.text_classification.api import (
    TextClassificationAnnotation,
    TextClassificationBulkData,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchRequest,
    TextClassificationSearchResults,
)

from tests.server.test_helpers import client


def test_create_records_for_text_classification_with_multi_label(monkeypatch):
    dataset = "test_create_records_for_text_classification_with_multi_label"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    records = [
        TextClassificationRecord.parse_obj(data)
        for data in [
            {
                "id": 0,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {
                    "field_one": "value one",
                    "field_two": "value 2",
                    "one_more": [{"a": 1, "b": 2}],
                },
                "prediction": {
                    "agent": "test",
                    "labels": [
                        {"class": "Test", "score": 0.6},
                        {"class": "Mocking", "score": 0.7},
                        {"class": "NoClass", "score": 0.2},
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
                        {"class": "Test", "score": 0.6},
                        {"class": "Mocking", "score": 0.7},
                        {"class": "NoClass", "score": 0.2},
                    ],
                },
            },
        ]
    ]
    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkData(
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
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkData(
            tags={"new": "tag"},
            metadata={"new": {"metadata": "value"}},
            records=records,
        ).dict(by_alias=True),
    )

    get_dataset = Dataset.parse_obj(client.get(f"/api/datasets/{dataset}").json())
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

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search", json={}
    )

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
    classification_bulk = TextClassificationBulkData(
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
                            {"class": "Test", "score": 0.3},
                            {"class": "Mocking", "score": 0.7},
                        ],
                    },
                }
            )
        ],
    )
    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
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

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search", json={}
    )

    assert response.status_code == 200
    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    assert results.aggregations.predicted_as == {"Mocking": 1}
    assert results.aggregations.status == {"Default": 1}
    assert results.aggregations.score
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
                    {"class": "Positive", "score": 0.6},
                    {"class": "Negative", "score": 0.3},
                    {"class": "Other", "score": 0.1},
                ],
            },
        }
    )

    bulk = TextClassificationBulkData(
        records=[record],
    )

    response = client.post(
        f"/api/datasets/{name}/TextClassification:bulk",
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

    client.post(
        f"/api/datasets/{name}/TextClassification:bulk",
        json=bulk.dict(by_alias=True),
    )

    response = client.post(
        f"/api/datasets/{name}/TextClassification:search",
        json={
            "query": TextClassificationQuery(predicted=PredictionStatus.OK).dict(
                by_alias=True
            ),
        },
    )

    assert response.status_code == 200
    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    first_record = results.records[0]
    assert first_record.last_updated is not None
    first_record.last_updated = None
    assert TextClassificationRecord(
        **first_record.dict(by_alias=True, exclude_none=True)
    ) == TextClassificationRecord(
        **{
            "id": 1,
            "inputs": {"text": "This is a text, oh yeah!"},
            "prediction": {
                "agent": "test",
                "labels": [
                    {"class": "Positive", "score": 0.6},
                    {"class": "Negative", "score": 0.3},
                    {"class": "Other", "score": 0.1},
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
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkData(
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
    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=0&limit=10",
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


def test_some_sort_by():
    dataset = "test_some_sort_by"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200
    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkData(
            records=[
                TextClassificationRecord(
                    **{
                        "id": i,
                        "inputs": {"data": "my data"},
                        "prediction": {"agent": f"agent_{i%5}", "labels": []},
                        "metadata": {
                            "s": f"{i} value",
                        },
                    }
                )
                for i in range(0, 100)
            ],
        ).dict(by_alias=True),
    )
    with pytest.raises(AssertionError):
        client.post(
            f"/api/datasets/{dataset}/TextClassification:search?from=0&limit=10",
            json={
                "sort": [
                    {"id": "wrong_field"},
                ]
            },
        )
    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=0&limit=10",
        json={
            "sort": [
                {"id": "predicted_by", "order": "desc"},
                {"id": "metadata.s", "order": "asc"},
            ]
        },
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert list(map(lambda r: r.id, results.records)) == [
        14,
        19,
        24,
        29,
        34,
        39,
        4,
        44,
        49,
        54,
    ]


def test_disable_aggregations_when_scroll():
    dataset = "test_disable_aggregations_when_scroll"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkData(
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
                                {"class": "Test", "score": 0.3},
                                {"class": "Mocking", "score": 0.7},
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

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=10",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert results.aggregations is None


def test_include_event_timestamp():
    dataset = "test_include_event_timestamp"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        data=TextClassificationBulkData(
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
                                {"class": "Test", "score": 0.3},
                                {"class": "Mocking", "score": 0.7},
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

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=10",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert all(map(lambda record: record.event_timestamp is not None, results.records))


def test_words_cloud():
    dataset = "test_language_detection"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        data=TextClassificationBulkData(
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

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.aggregations.words is not None


def test_metadata_with_point_in_field_name():
    dataset = "test_metadata_with_point_in_field_name"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        data=TextClassificationBulkData(
            records=[
                TextClassificationRecord(
                    **{
                        "id": 0,
                        "inputs": {"text": "Esto es un ejemplo de texto"},
                        "metadata": {"field.one": 1, "field.two": 2},
                    }
                ),
                TextClassificationRecord(
                    **{
                        "id": 1,
                        "inputs": {"text": "This is an simple text example"},
                        "metadata": {"field.one": 1, "field.two": 2},
                    }
                ),
            ],
        ).json(by_alias=True),
    )

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search?limit=0",
        json={},
    )

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert "field.one" in results.aggregations.metadata
    assert results.aggregations.metadata.get("field.one", {})["1"] == 2
    assert results.aggregations.metadata.get("field.two", {})["2"] == 2


def test_wrong_text_query():
    dataset = "test_wrong_text_query"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        data=TextClassificationBulkData(
            records=[
                TextClassificationRecord(
                    **{
                        "id": 0,
                        "inputs": {"text": "Esto es un ejemplo de texto"},
                        "metadata": {"field.one": 1, "field.two": 2},
                    }
                ),
            ],
        ).json(by_alias=True),
    )

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json=TextClassificationSearchRequest(
            query=TextClassificationQuery(query_text="!")
        ).dict(),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to parse query [!]"
