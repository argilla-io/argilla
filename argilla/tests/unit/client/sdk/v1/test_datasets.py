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
from uuid import UUID, uuid4

import httpx
import pytest
from argilla_v1.client.sdk.v1.datasets import api
from argilla_v1.client.sdk.v1.datasets.models import (
    FeedbackItemModel,
    FeedbackRecordSearchModel,
    FeedbackRecordsSearchModel,
    FeedbackRecordsSearchVectorQuery,
)


def test_search_records(mock_httpx_client: httpx.Client) -> None:
    json_response = {
        "items": [
            {
                "record": {
                    "id": str(uuid4()),
                    "fields": {},
                    "metadata": None,
                    "external_id": None,
                    "responses": [],
                    "suggestions": [],
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                "query_score": 1.0,
            },
            {
                "record": {
                    "id": str(uuid4()),
                    "fields": {},
                    "metadata": None,
                    "external_id": None,
                    "responses": [],
                    "suggestions": [],
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                "query_score": 0.5,
            },
        ],
        "total": 2,
    }

    mock_httpx_client.post.return_value = httpx.Response(status_code=200, json=json_response)

    dataset_id = uuid4()

    vector_query = FeedbackRecordsSearchVectorQuery(name="vector_name", value=[1.0, 2.0, 3.0])

    response = api.search_records(client=mock_httpx_client, id=dataset_id, vector_query=vector_query)

    assert response.status_code == 200
    assert response.parsed == FeedbackRecordsSearchModel(
        items=[
            FeedbackRecordSearchModel(
                record=FeedbackItemModel(
                    id=UUID(json_response["items"][0]["record"]["id"]),
                    fields={},
                    metadata=None,
                    external_id=None,
                    responses=[],
                    suggestions=[],
                    inserted_at=datetime.fromisoformat(json_response["items"][0]["record"]["inserted_at"]),
                    updated_at=datetime.fromisoformat(json_response["items"][0]["record"]["updated_at"]),
                ),
                query_score=1.0,
            ),
            FeedbackRecordSearchModel(
                record=FeedbackItemModel(
                    id=UUID(json_response["items"][1]["record"]["id"]),
                    fields={},
                    metadata=None,
                    external_id=None,
                    responses=[],
                    suggestions=[],
                    inserted_at=datetime.fromisoformat(json_response["items"][1]["record"]["inserted_at"]),
                    updated_at=datetime.fromisoformat(json_response["items"][1]["record"]["updated_at"]),
                ),
                query_score=0.5,
            ),
        ],
        total=2,
    )

    mock_httpx_client.post.assert_called_once_with(
        url=f"/api/v1/datasets/{dataset_id}/records/search",
        params={"limit": 50},
        json={"query": {"vector": {"name": "vector_name", "value": [1.0, 2.0, 3.0]}}},
    )


def test_search_records_with_record_id(mock_httpx_client: httpx.Client):
    json_response = {
        "items": [
            {
                "record": {
                    "id": str(uuid4()),
                    "fields": {},
                    "metadata": None,
                    "external_id": None,
                    "responses": [],
                    "suggestions": [],
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                "query_score": 1.0,
            },
            {
                "record": {
                    "id": str(uuid4()),
                    "fields": {},
                    "metadata": None,
                    "external_id": None,
                    "responses": [],
                    "suggestions": [],
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                "query_score": 0.5,
            },
        ],
        "total": 2,
    }

    mock_httpx_client.post.return_value = httpx.Response(status_code=200, json=json_response)

    dataset_id = uuid4()
    expected_record_id = uuid4()

    vector_query = FeedbackRecordsSearchVectorQuery(name="vector_name", record_id=expected_record_id)

    response = api.search_records(
        client=mock_httpx_client,
        id=dataset_id,
        vector_query=vector_query,
    )

    assert response.status_code == 200
    assert response.parsed == FeedbackRecordsSearchModel(
        items=[
            FeedbackRecordSearchModel(
                record=FeedbackItemModel(
                    id=UUID(json_response["items"][0]["record"]["id"]),
                    fields={},
                    metadata=None,
                    external_id=None,
                    responses=[],
                    suggestions=[],
                    inserted_at=datetime.fromisoformat(json_response["items"][0]["record"]["inserted_at"]),
                    updated_at=datetime.fromisoformat(json_response["items"][0]["record"]["updated_at"]),
                ),
                query_score=1.0,
            ),
            FeedbackRecordSearchModel(
                record=FeedbackItemModel(
                    id=UUID(json_response["items"][1]["record"]["id"]),
                    fields={},
                    metadata=None,
                    external_id=None,
                    responses=[],
                    suggestions=[],
                    inserted_at=datetime.fromisoformat(json_response["items"][1]["record"]["inserted_at"]),
                    updated_at=datetime.fromisoformat(json_response["items"][1]["record"]["updated_at"]),
                ),
                query_score=0.5,
            ),
        ],
        total=2,
    )

    mock_httpx_client.post.assert_called_once_with(
        url=f"/api/v1/datasets/{dataset_id}/records/search",
        params={"limit": 50},
        json={"query": {"vector": {"name": "vector_name", "record_id": str(expected_record_id)}}},
    )


def test_search_records_with_invalid_query(mock_httpx_client: httpx.Client):
    dataset_id = uuid4()

    with pytest.raises(ValueError, match="Either 'record_id' or 'value' must be provided"):
        vector_query = FeedbackRecordsSearchVectorQuery(name="vector_name", value=[1.0, 2.0, 3.0], record_id=uuid4())
        api.search_records(client=mock_httpx_client, id=dataset_id, vector_query=vector_query)
