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
from typing import TYPE_CHECKING

import pytest
from argilla_server.apis.v0.models.commons.model import BulkResponse
from argilla_server.apis.v0.models.text_classification import (
    TextClassificationAnnotation,
    TextClassificationBulkRequest,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchRequest,
    TextClassificationSearchResults,
)
from argilla_server.commons.models import PredictionStatus, TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User
from argilla_server.schemas.v0.datasets import Dataset

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_records_for_text_classification_with_multi_label(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_create_records_for_text_classification_with_multi_label"

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

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
                    "agent": "testA",
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
                "metadata": {
                    "field_one": "another value one",
                    "field_two": "value 2",
                },
                "prediction": {
                    "agent": "testB",
                    "labels": [
                        {"class": "Test", "score": 0.6},
                        {"class": "Mocking", "score": 0.7},
                        {"class": "NoClass", "score": 0.2},
                    ],
                },
            },
        ]
    ]
    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 2

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
            tags={"new": "tag"},
            metadata={"new": {"metadata": "value"}},
            records=records,
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    response = await async_client.get(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200, response.json()

    dataset_response = Dataset.parse_obj(response.json())
    assert dataset_response.tags == {"env": "test", "class": "text classification", "new": "tag"}
    assert dataset_response.metadata == {"config": {"the": "config"}, "new": {"metadata": "value"}}

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search", json={}, params=workspace_query_params
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 2
    assert results.aggregations.predicted_as == {"Mocking": 2, "Test": 2}
    assert results.records[0].predicted is None

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json={"query": {"predicted_by": ["testA"]}},
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == len(results.records) == 1
    assert results.aggregations.predicted_by == {"testA": 1}


@pytest.mark.asyncio
async def test_create_records_for_text_classification(async_client: "AsyncClient", argilla_user: User, test_telemetry):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_create_records_for_text_classification"

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    tags = {"env": "test", "class": "text classification"}
    metadata = {"config": {"the": "config"}}
    classification_bulk = TextClassificationBulkRequest(
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

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=classification_bulk.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 1

    response = await async_client.get(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    created_dataset = Dataset.parse_obj(response.json())
    assert created_dataset.tags == tags
    assert created_dataset.metadata == metadata

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search", json={}, params=workspace_query_params
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {},
        "annotated_by": {},
        "metadata": {},
        "predicted": {},
        "predicted_as": {"Mocking": 1},
        "predicted_by": {"test": 1},
        "status": {"Default": 1},
        "words": {"data": 1},
    }

    test_telemetry.track_data.assert_called()


@pytest.mark.asyncio
async def test_create_records_for_text_classification_vector_search(
    async_client: "AsyncClient", argilla_user: User, test_telemetry
):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_create_records_for_text_classification_vector_search"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    tags = {"env": "test", "class": "text classification"}
    metadata = {"config": {"the": "config"}}
    classification_bulk = TextClassificationBulkRequest(
        tags=tags,
        metadata=metadata,
        records=[
            TextClassificationRecord(**a)
            for a in [
                {
                    "id": 0,
                    "inputs": {"data": "my data"},
                    "prediction": {
                        "agent": "test",
                        "labels": [
                            {"class": "Test", "score": 0.3},
                            {"class": "Mocking", "score": 0.7},
                        ],
                    },
                    "vectors": {"my_bert": {"value": [10, 11, 12, 13]}},
                },
                {
                    "id": 1,
                    "inputs": {"data": "your data"},
                    "prediction": {
                        "agent": "test",
                        "labels": [
                            {"class": "Test", "score": 0.35},
                            {"class": "Mocking", "score": 0.65},
                        ],
                    },
                    "vectors": {"my_bert": {"value": [14, 15, 16, 17]}},
                },
                {
                    "id": 2,
                    "inputs": {"data": "their data"},
                    "prediction": {
                        "agent": "test",
                        "labels": [
                            {"class": "Test", "score": 0.4},
                            {"class": "Mocking", "score": 0.6},
                        ],
                    },
                    "vectors": {"my_bert": {"value": [14, 15, 16, 18]}},
                },
            ]
        ],
    )
    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=classification_bulk.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 3

    response = await async_client.get(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    created_dataset = Dataset.parse_obj(response.json())
    assert created_dataset.tags == tags
    assert created_dataset.metadata == metadata

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search", json={}, params=workspace_query_params
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 3
    assert all(hasattr(record, "vectors") for record in results.records)
    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {},
        "annotated_by": {},
        "metadata": {},
        "predicted": {},
        "predicted_as": {"Mocking": 3},
        "predicted_by": {"test": 3},
        "status": {"Default": 3},
        "words": {"data": 3},
    }

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json={
            "query": {
                "vector": {
                    "name": "my_bert",
                    "value": [14, 15, 16, 17],
                },
            }
        },
        params=workspace_query_params,
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 3
    assert all(hasattr(record, "vectors") for record in results.records)
    # similarity ordered records
    assert [record.id for record in results.records] == [1, 2, 0]


@pytest.mark.asyncio
async def test_partial_record_update(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    name = "test_partial_record_update"
    response = await async_client.delete(f"/api/datasets/{name}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": name, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

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

    bulk = TextClassificationBulkRequest(records=[record])

    response = await async_client.post(
        f"/api/datasets/{name}/TextClassification:bulk",
        json=bulk.dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.failed == 0
    assert bulk_response.processed == 1

    record.annotation = TextClassificationAnnotation.parse_obj(
        {"agent": "gold_standard", "labels": [{"class": "Positive"}]}
    )

    bulk.records = [record]
    await async_client.post(
        f"/api/datasets/{name}/TextClassification:bulk", json=bulk.dict(by_alias=True), params=workspace_query_params
    )

    response = await async_client.post(
        f"/api/datasets/{name}/TextClassification:search",
        json={"query": TextClassificationQuery(predicted=PredictionStatus.OK).dict(by_alias=True)},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1

    first_record = results.records[0]
    assert first_record.last_updated is not None

    first_record.last_updated = None
    assert TextClassificationRecord(**first_record.dict(by_alias=True, exclude_none=True)) == TextClassificationRecord(
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


@pytest.mark.asyncio
async def test_sort_by_last_updated(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_sort_by_last_updated"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    for i in range(0, 10):
        response = await async_client.post(
            f"/api/datasets/{dataset}/TextClassification:bulk",
            json=TextClassificationBulkRequest(
                records=[
                    TextClassificationRecord(
                        **{
                            "id": i,
                            "inputs": {"data": "my data"},
                            "metadata": {"s": "value"},
                        }
                    )
                ],
            ).dict(by_alias=True),
            params=workspace_query_params,
        )
        assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=0&limit=10",
        json={"sort": [{"id": "last_updated", "order": "asc"}]},
        params=workspace_query_params,
    )
    assert response.status_code == 200
    assert [r["id"] for r in response.json()["records"]] == list(range(0, 10))


@pytest.mark.asyncio
async def test_sort_by_id_as_default(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_sort_by_id_as_default"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
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
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=0&limit=10", json={}, params=workspace_query_params
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert list(map(lambda r: r.id, results.records)) == [0, 1, 10, 11, 12, 13, 14, 15, 16, 17]


@pytest.mark.asyncio
async def test_some_sort_by(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_some_sort_by"
    expected_records_length = 50

    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
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
                for i in range(0, expected_records_length)
            ],
        ).dict(by_alias=True),
        params=workspace_query_params,
    )

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=0&limit=10",
        json={
            "sort": [
                {"id": "wrong_field"},
            ]
        },
        params=workspace_query_params,
    )
    assert response.status_code == 400

    expected_response_property_name_2_value = {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "Wrong sort id wrong_field. Valid values "
                "are: ['id', 'metadata', 'score', "
                "'predicted', 'predicted_as', "
                "'predicted_by', 'annotated_as', "
                "'annotated_by', 'status', 'last_updated', "
                "'event_timestamp']"
            },
        }
    }
    assert response.json()["detail"]["code"] == expected_response_property_name_2_value["detail"]["code"]
    assert (
        response.json()["detail"]["params"]["message"]
        == expected_response_property_name_2_value["detail"]["params"]["message"]
    )
    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=0&limit=10",
        json={
            "sort": [
                {"id": "predicted_by", "order": "desc"},
                {"id": "metadata.s", "order": "asc"},
            ]
        },
        params=workspace_query_params,
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == expected_records_length
    assert list(map(lambda r: r.id, results.records)) == [14, 19, 24, 29, 34, 39, 4, 44, 49, 9]


@pytest.mark.asyncio
async def test_disable_aggregations_when_scroll(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_disable_aggregations_when_scroll"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)

    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
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
        params=workspace_query_params,
    )
    assert response.status_code == 200

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.processed == 100

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=10",
        json={},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert results.aggregations is None


@pytest.mark.asyncio
async def test_include_event_timestamp(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_include_event_timestamp"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200
    request = TextClassificationBulkRequest(
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
                        "labels": [{"class": "Test", "score": 0.3}, {"class": "Mocking", "score": 0.7}],
                    },
                }
            )
            for i in range(0, 100)
        ],
    )
    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        # Use content instead of json to properly serialize event_timestamp datetime
        content=request.json(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.processed == 100

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search?from=10", json={}, params=workspace_query_params
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 100
    assert all(map(lambda record: record.event_timestamp is not None, results.records))


@pytest.mark.asyncio
async def test_words_cloud(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_language_detection"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)

    assert response.status_code == 200
    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
            records=[
                TextClassificationRecord(**{"id": 0, "inputs": {"text": "Esto es un ejemplo de texto"}}),
                TextClassificationRecord(**{"id": 1, "inputs": {"text": "This is an simple text example"}}),
                TextClassificationRecord(**{"id": 2, "inputs": {"text": "C'est nes pas une pipe"}}),
            ],
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    BulkResponse.parse_obj(response.json())
    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search", json={}, params=workspace_query_params
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.aggregations.words is not None


@pytest.mark.asyncio
async def test_metadata_with_point_in_field_name(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_metadata_with_point_in_field_name"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
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
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search?limit=0", json={}, params=workspace_query_params
    )
    assert response.status_code == 200

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert "field.one" in results.aggregations.metadata
    assert results.aggregations.metadata.get("field.one", {})["1"] == 2
    assert results.aggregations.metadata.get("field.two", {})["2"] == 2


@pytest.mark.asyncio
async def test_wrong_text_query(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_wrong_text_query"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
            records=[
                TextClassificationRecord(
                    **{
                        "id": 0,
                        "inputs": {"text": "Esto es un ejemplo de texto"},
                        "metadata": {"field.one": 1, "field.two": 2},
                    }
                ),
            ],
        ).dict(by_alias=True),
        params=workspace_query_params,
    )

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json=TextClassificationSearchRequest(query=TextClassificationQuery(query_text="!")).dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 400

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::InvalidTextSearchError",
            "params": {"message": "Failed to parse query [!]"},
        }
    }


@pytest.mark.asyncio
async def test_search_using_text(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_search_using_text"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset, "task": TaskType.text_classification, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
            records=[
                TextClassificationRecord(
                    **{
                        "id": 0,
                        "inputs": {"data": "Esto es un ejemplo de Texto"},
                        "metadata": {"field.one": 1, "field.two": 2},
                    }
                ),
            ],
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json=TextClassificationSearchRequest(query=TextClassificationQuery(query_text="text: texto")).dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    assert response.json()["total"] == 1

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search",
        json=TextClassificationSearchRequest(query=TextClassificationQuery(query_text="text.exact: texto")).dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    assert response.json()["total"] == 0
