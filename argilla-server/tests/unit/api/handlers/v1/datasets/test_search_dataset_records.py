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
from argilla_server.api.handlers.v1.datasets.records import LIST_DATASET_RECORDS_LIMIT_LE
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import RecordInclude, SortOrder, RecordStatus
from argilla_server.search_engine import (
    AndFilter,
    Order,
    RangeFilter,
    ResponseFilterScope,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    SuggestionFilterScope,
    TermsFilter,
)
from httpx import AsyncClient

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    OwnerFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    VectorFactory,
    VectorSettingsFactory,
)


@pytest.mark.asyncio
class TestSearchDatasetRecords:
    def url(self, dataset_id: UUID) -> str:
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
                        "status": RecordStatus.pending,
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
                                "record_id": str(record_a.id),
                                "user_id": str(response_a.user_id),
                                "inserted_at": response_a.inserted_at.isoformat(),
                                "updated_at": response_a.updated_at.isoformat(),
                            },
                            {
                                "id": str(response_b.id),
                                "status": "submitted",
                                "values": {"input_ok": {"value": "no"}},
                                "record_id": str(record_a.id),
                                "user_id": str(response_b.user_id),
                                "inserted_at": response_b.inserted_at.isoformat(),
                                "updated_at": response_b.updated_at.isoformat(),
                            },
                        ],
                        "external_id": record_a.external_id,
                        "dataset_id": str(record_a.dataset_id),
                        "inserted_at": record_a.inserted_at.isoformat(),
                        "updated_at": record_a.updated_at.isoformat(),
                    },
                    "query_score": 1.0,
                },
                {
                    "record": {
                        "id": str(record_b.id),
                        "status": RecordStatus.pending,
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
                                "record_id": str(record_b.id),
                                "user_id": str(response_c.user_id),
                                "inserted_at": response_c.inserted_at.isoformat(),
                                "updated_at": response_c.updated_at.isoformat(),
                            },
                        ],
                        "external_id": record_b.external_id,
                        "dataset_id": str(record_b.dataset_id),
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

    async def test_with_non_existent_dataset(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset_id = uuid4()

        response = await async_client.post(
            self.url(dataset_id),
            headers=owner_auth_header,
            json={"query": {"text": {"q": "text"}}},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Dataset with id `{dataset_id}` not found"}

    async def test_with_text_query_using_non_existent_field(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"query": {"text": {"q": "text", "field": "non-existent"}}},
        )

        assert response.status_code == 422

    async def test_with_vector_query_using_record_without_vector(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await TextFieldFactory.create(name="input", dataset=dataset)
        vector_settings = await VectorSettingsFactory.create(name="vector", dimensions=3, dataset=dataset)

        record = await RecordFactory.create(dataset=dataset)
        record_without_vector = await RecordFactory.create(dataset=dataset)

        await VectorFactory.create(value=[1.0, 2.0, 3.0], vector_settings=vector_settings, record=record)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "query": {
                    "vector": {
                        "name": vector_settings.name,
                        "record_id": str(record_without_vector.id),
                    },
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "code": "missing_vector",
            "message": f"Record `{record_without_vector.id}` does not have a vector for vector settings `{vector_settings.name}`",
        }

    async def test_with_filter(
        self, async_client: AsyncClient, mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        question = await RatingQuestionFactory.create(dataset=dataset)

        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)

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
            json={
                "filters": {
                    "and": [
                        {
                            "type": "terms",
                            "scope": {"entity": "response", "question": question.name},
                            "values": ["value-a"],
                        },
                        {
                            "type": "range",
                            "scope": {"entity": "suggestion", "question": question.name, "property": "score"},
                            "ge": 0.5,
                        },
                    ],
                },
            },
        )

        assert response.status_code == 200

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            filter=AndFilter(
                filters=[
                    TermsFilter(scope=ResponseFilterScope(question=question.name), values=["value-a"]),
                    RangeFilter(scope=SuggestionFilterScope(question=question.name, property="score"), ge=0.5),
                ]
            ),
            offset=0,
            limit=50,
            query=None,
        )

    async def test_with_sort(
        self, async_client: AsyncClient, mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        question = await RatingQuestionFactory.create(dataset=dataset)

        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)

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
            json={
                "sort": [
                    {
                        "scope": {"entity": "response", "question": question.name},
                        "order": "asc",
                    },
                    {
                        "scope": {"entity": "suggestion", "question": question.name, "property": "score"},
                        "order": "desc",
                    },
                ]
            },
        )

        assert response.status_code == 200

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            sort=[
                Order(scope=ResponseFilterScope(question=question.name), order=SortOrder.asc),
                Order(scope=SuggestionFilterScope(question=question.name, property="score"), order=SortOrder.desc),
            ],
            offset=0,
            limit=50,
            query=None,
        )

    async def test_with_invalid_filter(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "filters": {
                    "and": [
                        {
                            "type": "terms",
                            "scope": {"entity": "response", "question": "non-existent"},
                            "values": ["value-a"],
                        }
                    ],
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Question not found filtering by name=non-existent, dataset_id={dataset.id}"
        }

    async def test_with_invalid_sort(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "query": {
                    "text": {"q": "text", "field": "non-existent"},
                },
                "sort": [{"scope": {"entity": "response", "question": "non-existent"}, "order": "asc"}],
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Question not found filtering by name=non-existent, dataset_id={dataset.id}"
        }
