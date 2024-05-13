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
from typing import TYPE_CHECKING, List, Optional

import pytest
from argilla_server.apis.v0.models.commons.model import BulkResponse
from argilla_server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextRecordInputs,
    Text2TextSearchResults,
)
from argilla_server.commons.models import TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_records(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_search_records"
    await delete_dataset(async_client, dataset, workspace_name=argilla_user.username)

    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.text2text.value, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    records = [
        Text2TextRecordInputs.parse_obj(data)
        for data in [
            {
                "id": 0,
                "text": "This is a text data",
                "metadata": {"field_one": "value one"},
                "prediction": {"agent": "test", "sentences": [{"text": "This is a test data", "score": 0.6}]},
            },
            {"id": 1, "text": "Ånother data"},
        ]
    ]
    response = await async_client.post(
        f"/api/datasets/{dataset}/Text2Text:bulk",
        json=Text2TextBulkRequest(
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
        f"/api/datasets/{dataset}/Text2Text:search", json={}, params=workspace_query_params
    )
    assert response.status_code == 200, response.json()

    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == 2
    assert results.records[0].predicted is None

    assert results.aggregations.dict(exclude={"score"}) == {
        "annotated_as": {},
        "annotated_by": {},
        "annotated_text": {},
        "metadata": {"field_one": {"value one": 1}},
        "predicted": {},
        "predicted_as": {},
        "predicted_by": {"test": 1},
        "predicted_text": {},
        "status": {"Default": 2},
        "words": {"data": 2, "text": 1, "ånother": 1},
    }


async def search_data(
    *,
    async_client: "AsyncClient",
    base_url: str,
    workspace_name: str,
    expected_total: int,
    body: Optional[dict] = None,
    vector_name: Optional[str] = None,
):
    response = await async_client.post(url=f"{base_url}:search", json=body or {}, params={"workspace": workspace_name})
    assert response.status_code == 200, response.json()

    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == expected_total
    for record in results.records:
        if vector_name:
            assert record.vectors is not None
            assert vector_name in record.vectors


@pytest.mark.asyncio
async def test_search_with_vectors(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_search_with_vectors"

    await delete_dataset(async_client, dataset, workspace_name=argilla_user.username)
    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.text2text.value, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    records_for_text2text_with_vectors = [
        Text2TextRecordInputs.parse_obj(data)
        for data in [
            {
                "id": 0,
                "text": "This is a text data",
                "metadata": {"field_one": "value one"},
                "prediction": {"agent": "test", "sentences": [{"text": "This is a test data", "score": 0.6}]},
                "vectors": {"my_bert": {"value": [1, 2, 3, 4]}},
            },
            {
                "id": 1,
                "text": "Ånother data",
                "vectors": {"my_bert": {"value": [4, 5, 6, 7]}},
            },
            {
                "id": 3,
                "text": "This is another text data",
                "prediction": {"agent": "test", "sentences": [{"text": "This is another test data", "score": 0.6}]},
            },
        ]
    ]

    base_url = await prepare_data(
        async_client=async_client,
        dataset=dataset,
        workspace_name=argilla_user.username,
        records=records_for_text2text_with_vectors,
    )

    await search_data(
        async_client=async_client,
        workspace_name=argilla_user.username,
        base_url=base_url,
        expected_total=2,
        vector_name="my_bert",
        body={
            "query": {
                "vector": {
                    "name": "my_bert",
                    "value": [1.2, 2.3, 4.1, 6.1],
                }
            }
        },
    )


@pytest.mark.asyncio
async def test_api_with_new_predictions_data_model(async_client: "AsyncClient", argilla_user: User):
    async_client.headers.update({API_KEY_HEADER_NAME: argilla_user.api_key})
    workspace_query_params = {"workspace": argilla_user.username}

    dataset = "test_api_with_new_predictions_data_model"
    await delete_dataset(async_client, dataset, workspace_name=argilla_user.username)
    response = await async_client.post(
        "/api/datasets",
        json={"name": dataset, "task": TaskType.text2text.value, "workspace": argilla_user.username},
        params=workspace_query_params,
    )
    assert response.status_code == 200

    records = [
        Text2TextRecordInputs.parse_obj(
            {
                "text": "This is a text data",
                "predictions": {"test": {"sentences": [{"text": "This is a test data", "score": 0.6}]}},
            }
        ),
        Text2TextRecordInputs.parse_obj(
            {
                "text": "Another data",
                "annotations": {
                    "annotator-1": {"sentences": [{"text": "THis is a test data"}]},
                    "annotator-2": {"sentences": [{"text": "This IS the test datay"}]},
                },
            }
        ),
    ]

    await prepare_data(
        async_client=async_client, dataset=dataset, workspace_name=argilla_user.username, records=records
    )

    response = await async_client.post(
        f"/api/datasets/{dataset}/Text2Text:search",
        json={"query": {"query_text": "predictions.test.sentences.text.exact:data"}},
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == 1, results

    response = await async_client.post(
        f"/api/datasets/{dataset}/Text2Text:search",
        json={"query": {"query_text": "_exists_:annotations.annotator-1"}},
        params=workspace_query_params,
    )
    assert response.status_code == 200, response.json()

    results = Text2TextSearchResults.parse_obj(response.json())
    assert results.total == 1, results


async def prepare_data(
    *, async_client: "AsyncClient", dataset: str, workspace_name: str, records: List[Text2TextRecordInputs]
):
    base_api_url = f"/api/datasets/{dataset}/Text2Text"
    response = await async_client.post(
        f"{base_api_url}:bulk",
        json=Text2TextBulkRequest(
            records=records,
        ).dict(by_alias=True),
        params={"workspace": workspace_name},
    )
    assert response.status_code == 200, response.json()

    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == len(records)

    return base_api_url


async def delete_dataset(async_client: "AsyncClient", dataset: str, workspace_name: str):
    response = await async_client.delete(f"/api/datasets/{dataset}", params={"workspace": workspace_name})
    assert response.status_code == 200
