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

import uuid

import httpx
import pytest
from argilla_v1.client.sdk.commons.errors import ArApiResponseError
from argilla_v1.client.sdk.v1.datasets.api import search_records
from argilla_v1.client.sdk.v1.datasets.models import FeedbackRecordsSearchVectorQuery


class TestSuiteSearchRecordsSDK:
    def test_search_records_with_record_api_call(self, mock_httpx_client: httpx.Client):
        dataset_id = uuid.uuid4()
        query = FeedbackRecordsSearchVectorQuery(name="test-vector", record_id=uuid.uuid4())
        max_results = 100

        mock_httpx_client.post.return_value = httpx.Response(status_code=200, json={"total": 0, "items": []})

        search_records(client=mock_httpx_client, id=dataset_id, vector_query=query, limit=max_results)

        mock_httpx_client.post.assert_called_once_with(
            url=f"/api/v1/datasets/{dataset_id}/records/search",
            params={"limit": max_results},
            json={"query": {"vector": {"name": query.name, "record_id": str(query.record_id)}}},
        )

    def test_search_records_with_value_api_call(self, mock_httpx_client: httpx.Client):
        dataset_id = uuid.uuid4()
        query = FeedbackRecordsSearchVectorQuery(name="test-vector", value=[1, 2, 3])
        max_results = 5

        mock_httpx_client.post.return_value = httpx.Response(status_code=200, json={"total": 0, "items": []})

        search_records(client=mock_httpx_client, id=dataset_id, vector_query=query, limit=max_results)

        mock_httpx_client.post.assert_called_once_with(
            url=f"/api/v1/datasets/{dataset_id}/records/search",
            params={"limit": max_results},
            json={"query": {"vector": {"name": query.name, "value": query.value}}},
        )

    def test_search_records_with_filters(self, mock_httpx_client: httpx.Client):
        dataset_id = uuid.uuid4()
        query = FeedbackRecordsSearchVectorQuery(name="test-vector", value=[1, 2, 3])
        expected_metadata_filters = ["metadata1:3", "metadata2:4"]
        max_results = 5

        mock_httpx_client.post.return_value = httpx.Response(status_code=200, json={"total": 0, "items": []})

        search_records(
            client=mock_httpx_client,
            id=dataset_id,
            vector_query=query,
            limit=max_results,
            metadata_filters=expected_metadata_filters,
        )

        mock_httpx_client.post.assert_called_once_with(
            url=f"/api/v1/datasets/{dataset_id}/records/search",
            params={
                "limit": max_results,
                "metadata": expected_metadata_filters,
            },
            json={"query": {"vector": {"name": query.name, "value": query.value}}},
        )

    @pytest.mark.parametrize(
        "status_code, error_detail",
        [
            (400, "Some mock error"),
            (422, "Wrong query format"),
            (500, "Unexpected error"),
            (405, "Method not allowed"),
            (418, "Are you a teapot?"),
        ],
    )
    def test_search_records_with_api_error(self, mock_httpx_client: httpx.Client, status_code: int, error_detail: str):
        dataset_id = uuid.uuid4()
        query = FeedbackRecordsSearchVectorQuery(name="test-vector", value=[1, 2, 3])
        max_results = 5

        mock_httpx_client.post.return_value = httpx.Response(status_code=status_code, json={"detail": error_detail})

        with pytest.raises(ArApiResponseError, match=error_detail) as exc_info:
            search_records(client=mock_httpx_client, id=dataset_id, vector_query=query, limit=max_results)

        assert exc_info.value.HTTP_STATUS == status_code

    def test_search_records_with_include(self, mock_httpx_client: httpx.Client):
        dataset_id = uuid.uuid4()
        query = FeedbackRecordsSearchVectorQuery(name="test-vector", value=[1, 2])
        max_results = 5

        mock_httpx_client.post.return_value = httpx.Response(status_code=200, json={"total": 0, "items": []})

        search_records(
            client=mock_httpx_client,
            id=dataset_id,
            vector_query=query,
            limit=max_results,
            include=["metadata", "responses", "vectors:v1"],
        )

        mock_httpx_client.post.assert_called_once_with(
            url=f"/api/v1/datasets/{dataset_id}/records/search",
            params={"include": ["metadata", "responses", "vectors:v1"], "limit": max_results},
            json={"query": {"vector": {"name": query.name, "value": query.value}}},
        )
