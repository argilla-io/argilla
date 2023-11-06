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

from uuid import UUID, uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.apis.v1.handlers.datasets import LIST_DATASET_RECORDS_LIMIT_LE
from argilla.server.enums import RecordInclude
from argilla.server.search_engine import SearchEngine, SearchResponseItem, SearchResponses
from httpx import AsyncClient

from tests.factories import AdminFactory, AnnotatorFactory, DatasetFactory, OwnerFactory, RecordFactory, ResponseFactory


@pytest.mark.asyncio
class TestSearchDatasetRecords:
    def url(self, dataset_id: UUID):
        return f"/api/v1/datasets/{dataset_id}/records/search"

    async def test_as_owner(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        owner = await OwnerFactory.create(workspaces=[dataset.workspace])

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: owner.api_key},
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 200

    async def test_as_admin_from_different_workspace(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        admin = await AdminFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 403

    async def test_as_annotator(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 403

    async def test_with_include_responses(
        self, async_client: AsyncClient, owner_auth_header: dict, mock_search_engine: SearchEngine
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)

        response_a = await ResponseFactory.create(values={"input_ok": {"value": "yes"}}, record=record_a)
        response_b = await ResponseFactory.create(values={"input_ok": {"value": "no"}}, record=record_a)
        response_c = await ResponseFactory.create(values={"input_ok": {"value": "yes"}}, record=record_b)

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=record_a.id, score=1.0),
                SearchResponseItem(record_id=record_b.id, score=0.5),
            ],
            total=2,
        )

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            params={"include": RecordInclude.responses.value},
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "record": {
                        "id": str(record_a.id),
                        "fields": {
                            "sentiment": "neutral",
                            "text": "This is a text",
                        },
                        "metadata": None,
                        "responses": [
                            {
                                "id": str(response_a.id),
                                "status": "submitted",
                                "values": {"input_ok": {"value": "yes"}},
                                "user_id": str(response_a.user_id),
                                "inserted_at": response_a.inserted_at.isoformat(),
                                "updated_at": response_a.updated_at.isoformat(),
                            },
                            {
                                "id": str(response_b.id),
                                "status": "submitted",
                                "values": {"input_ok": {"value": "no"}},
                                "user_id": str(response_b.user_id),
                                "inserted_at": response_b.inserted_at.isoformat(),
                                "updated_at": response_b.updated_at.isoformat(),
                            },
                        ],
                        "external_id": record_a.external_id,
                        "inserted_at": record_a.inserted_at.isoformat(),
                        "updated_at": record_a.updated_at.isoformat(),
                    },
                    "query_score": 1.0,
                },
                {
                    "record": {
                        "id": str(record_b.id),
                        "fields": {
                            "sentiment": "neutral",
                            "text": "This is a text",
                        },
                        "metadata": None,
                        "responses": [
                            {
                                "id": str(response_c.id),
                                "status": "submitted",
                                "values": {"input_ok": {"value": "yes"}},
                                "user_id": str(response_c.user_id),
                                "inserted_at": response_c.inserted_at.isoformat(),
                                "updated_at": response_c.updated_at.isoformat(),
                            },
                        ],
                        "external_id": record_b.external_id,
                        "inserted_at": record_b.inserted_at.isoformat(),
                        "updated_at": record_b.updated_at.isoformat(),
                    },
                    "query_score": 0.5,
                },
            ],
            "total": 2,
        }

    async def test_with_invalid_offset(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.post(
            self.url(uuid4()),
            headers=owner_auth_header,
            params={"offset": -1},
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 422

    async def test_with_invalid_lower_limit(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.post(
            self.url(uuid4()),
            headers=owner_auth_header,
            params={"limit": 0},
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 422

    async def test_with_invalid_upper_limit(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.post(
            self.url(uuid4()),
            headers=owner_auth_header,
            params={"limit": LIST_DATASET_RECORDS_LIMIT_LE + 1},
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 422

    async def test_with_non_existent_field(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"query": {"text": {"q": "text", "field": "non-existent"}}},
        )

        assert response.status_code == 422

    async def test_with_non_existent_dataset(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.post(
            self.url(uuid4()),
            headers=owner_auth_header,
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 404
