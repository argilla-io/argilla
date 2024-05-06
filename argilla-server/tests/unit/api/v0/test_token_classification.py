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
from typing import Callable

import pytest
from argilla_server.apis.v0.models.commons.model import BulkResponse, SortableField
from argilla_server.apis.v0.models.token_classification import (
    TokenClassificationBulkRequest,
    TokenClassificationQuery,
    TokenClassificationRecord,
    TokenClassificationSearchRequest,
    TokenClassificationSearchResults,
)
from argilla_server.commons.models import TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User


@pytest.mark.asyncio
async def test_load_as_different_task(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_load_as_different_task"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": argilla_user.username, "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    expected_text = "This is a text with !"
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [{"tokens": expected_text.split(" "), "raw_text": expected_text}]
    ]
    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TextClassification:search", json={}, params=workspace_query_params
    )
    assert response.status_code == 400

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::WrongTaskError",
            "params": {"message": "Provided task TextClassification cannot be " "applied to dataset"},
        }
    }


@pytest.mark.asyncio
async def test_search_special_characters(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_search_special_characters"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": argilla_user.username, "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    expected_text = "This is a text with !"
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [{"tokens": expected_text.split(" "), "raw_text": expected_text}]
    ]
    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json=TokenClassificationSearchRequest(query=TokenClassificationQuery(query_text="\!")).dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert results.total == 0

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json=TokenClassificationSearchRequest(query=TokenClassificationQuery(query_text="text.exact:\!")).dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1


@pytest.mark.asyncio
async def test_some_sort(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_some_sort"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": argilla_user.username, "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    expected_text = "This is a text with !"
    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [{"tokens": expected_text.split(" "), "raw_text": expected_text}]
    ]
    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json=TokenClassificationSearchRequest(sort=[SortableField(id="babba")]).dict(),
        params=workspace_query_params,
    )
    assert response.status_code == 400

    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "Wrong sort id babba. Valid values are: "
                "['id', 'metadata', 'score', 'predicted', "
                "'predicted_as', 'predicted_by', "
                "'annotated_as', 'annotated_by', 'status', "
                "'last_updated', 'event_timestamp']"
            },
        }
    }


@pytest.mark.parametrize(
    ("include_metrics", "metrics_validator"),
    [
        (True, lambda r: len(r.metrics) > 0),
        (False, lambda r: len(r.metrics) == 0),
        (None, lambda r: len(r.metrics) == 0),
    ],
)
@pytest.mark.asyncio
async def test_create_records_for_token_classification(
    async_client: "AsyncClient", argilla_user: User, include_metrics: bool, metrics_validator: Callable
):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_create_records_for_token_classification"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": argilla_user.username, "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    entity_label = "TEST"
    expected_records = 2
    record = {
        "tokens": "This is a text".split(" "),
        "raw_text": "This is a text",
        "metadata": {"field_one": "value one", "field_two": "value 2"},
        "prediction": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
        "annotation": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
    }
    records = [TokenClassificationRecord.parse_obj(record)] * expected_records

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
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
    assert bulk_response.processed == expected_records

    params = {**workspace_query_params}
    if include_metrics is not None:
        params["include_metrics"] = include_metrics

    response = await async_client.post(f"/api/datasets/{dataset}/TokenClassification:search", params=params)
    assert response.status_code == 200, response.json()

    results = TokenClassificationSearchResults.parse_obj(response.json())

    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {"TEST": 1},
        "annotated_by": {"test": 1},
        "mentions": {"TEST": {"This": 1}},
        "metadata": {"field_one": {"value one": 1}, "field_two": {"value 2": 1}},
        "predicted": {"ok": 1},
        "predicted_as": {"TEST": 1},
        "predicted_by": {"test": 1},
        "predicted_mentions": {"TEST": {"This": 1}},
        "status": {"Default": 1},
        "words": {"text": 1},
    }

    assert "This" in results.aggregations.predicted_mentions[entity_label]
    assert "This" in results.aggregations.mentions[entity_label]
    for record in results.records:
        assert metrics_validator(record)


@pytest.mark.parametrize(
    ("include_metrics", "metrics_validator"),
    [
        (True, lambda r: len(r.metrics) > 0),
        (False, lambda r: len(r.metrics) == 0),
        (None, lambda r: len(r.metrics) == 0),
    ],
)
@pytest.mark.asyncio
async def test_create_records_for_token_classification_vector_search(
    async_client: "AsyncClient", argilla_user: User, include_metrics: bool, metrics_validator: Callable
):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_create_records_for_token_classification_vector_search"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": argilla_user.username, "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    entity_label = "TEST"
    expected_records = 3
    record_dicts = [
        {
            "id": 0,
            "tokens": "This is a text".split(" "),
            "raw_text": "This is a text",
            "metadata": {"field_one": "value one", "field_two": "value 2"},
            "prediction": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
            "annotation": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
            "vectors": {"my_bert": {"value": [1, 2, 3, 4, 5, 6]}},
        },
        {
            "id": 1,
            "tokens": "This is a text".split(" "),
            "raw_text": "This is a text",
            "metadata": {"field_one": "value one", "field_two": "value 2"},
            "prediction": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
            "annotation": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
            "vectors": {"my_bert": {"value": [5, 6, 7, 8, 9, 10]}},
        },
        {
            "id": 2,
            "tokens": "This is a text".split(" "),
            "raw_text": "This is a text",
            "metadata": {"field_one": "value one", "field_two": "value 2"},
            "prediction": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
            "annotation": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_label}]},
            "vectors": {"my_bert": {"value": [7, 8, 9, 10, 11, 12]}},
        },
    ]

    records = [TokenClassificationRecord.parse_obj(record) for record in record_dicts]

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
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
    assert bulk_response.processed == expected_records

    params = {**workspace_query_params}
    if include_metrics is not None:
        params["include_metrics"] = include_metrics

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json={"query": {"vector": {"name": "my_bert", "value": [5, 6, 7, 8, 9, 10]}}},
        params=params,
    )
    assert response.status_code == 200, response.json()

    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {"TEST": 3},
        "annotated_by": {"test": 3},
        "mentions": {"TEST": {"This": 3}},
        "metadata": {"field_one": {"value one": 3}, "field_two": {"value 2": 3}},
        "predicted": {"ok": 3},
        "predicted_as": {"TEST": 3},
        "predicted_by": {"test": 3},
        "predicted_mentions": {"TEST": {"This": 3}},
        "status": {"Default": 3},
        "words": {"text": 3},
    }

    assert "This" in results.aggregations.predicted_mentions[entity_label]
    assert "This" in results.aggregations.mentions[entity_label]

    expected_record_ids = [1, 2, 0]
    for index, record in enumerate(results.records):
        assert metrics_validator(record)
        assert expected_record_ids[index] == record.id
        assert hasattr(record, "vectors")


@pytest.mark.asyncio
async def test_multiple_mentions_in_same_record(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_multiple_mentions_in_same_record"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": argilla_user.username, "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

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
                    "entities": [{"start": 0, "end": 4, "label": entity_a}, {"start": 5, "end": 7, "label": entity_b}],
                },
            },
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "prediction": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_a}]},
            },
            {
                "tokens": "This is a text".split(" "),
                "raw_text": "This is a text",
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "annotation": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": entity_a}]},
            },
        ]
    ]
    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
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
    assert bulk_response.processed == 3

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search", params=workspace_query_params
    )
    assert response.status_code == 200, response.json()

    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert "This" in results.aggregations.predicted_mentions[entity_a]
    assert results.aggregations.predicted_mentions[entity_a]["This"] == 2
    assert "is" in results.aggregations.predicted_mentions[entity_b]
    assert results.aggregations.predicted_mentions[entity_b]["is"] == 1


@pytest.mark.asyncio
async def test_show_not_aggregable_metadata_fields(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_show_not_aggregable_metadata_fields"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": argilla_user.username, "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            records=[
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 1.3, "field_two": 2},
                    }
                ),
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 2.3, "field_two": 300},
                    },
                ),
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 11.333, "field_two": -10},
                    },
                ),
            ],
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search", json={}, params=workspace_query_params
    )
    assert response.status_code == 200, response.json()

    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert len(results.aggregations.metadata) == 2
    assert "field_one" in results.aggregations.metadata
    assert "argilla:stats" in results.aggregations.metadata["field_one"]


@pytest.mark.asyncio
async def test_search_with_raw_query(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = await log_some_data_for_token_classification(async_client, workspace_name=argilla_user.username)

    raw_es_query_matching_all = {
        "bool": {
            "filter": {
                "bool": {
                    "must": {"script": {"script": {"source": "doc['tokens'].value.length() == 4", "lang": "painless"}}}
                }
            }
        }
    }

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:search",
        json={"query": {"raw_query": raw_es_query_matching_all}},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    results = TokenClassificationSearchResults.parse_obj(response.json())
    assert len(results.records) == 3


async def log_some_data_for_token_classification(async_client: "AsyncClient", workspace_name: str):
    workspace_query_params = {"workspace": workspace_name}

    dataset = "log_some_data_for_token_classification"
    response = await async_client.delete(f"/api/datasets/{dataset}", params=workspace_query_params)
    assert response.status_code == 200

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "workspace": "argilla", "task": TaskType.token_classification.value},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=TokenClassificationBulkRequest(
            records=[
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 1.3, "field_two": 2},
                    },
                ),
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 2.3, "field_two": 300},
                    },
                ),
                TokenClassificationRecord.parse_obj(
                    {
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": 11.333, "field_two": -10},
                    },
                ),
            ],
        ).dict(by_alias=True),
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    return dataset
