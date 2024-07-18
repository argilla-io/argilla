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

from uuid import UUID

import pytest
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import UserRole, RecordStatus
from argilla_server.search_engine import SearchEngine, SearchResponseItem, SearchResponses
from httpx import AsyncClient

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    RecordFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    VectorFactory,
    VectorSettingsFactory,
    WorkspaceUserFactory,
)


@pytest.mark.asyncio
class TestSearchCurrentUserDatasetRecords:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/me/datasets/{dataset_id}/records/search"

    async def test_search_with_filtered_metadata(
        self, async_client: AsyncClient, mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await TextFieldFactory.create(name="input", dataset=dataset)
        await TermsMetadataPropertyFactory.create(
            name="annotator_meta", dataset=dataset, allowed_roles=[UserRole.admin, UserRole.annotator]
        )
        await TermsMetadataPropertyFactory.create(name="admin_meta", dataset=dataset, allowed_roles=[UserRole.admin])
        await TermsMetadataPropertyFactory.create(name="owner_meta", dataset=dataset, allowed_roles=[])
        record = await RecordFactory.create(
            metadata_={"admin_meta": "value", "annotator_meta": "value", "owner_meta": "value", "extra": "value"},
            dataset=dataset,
        )

        mock_search_engine.search.return_value = SearchResponses(
            items=[SearchResponseItem(record_id=record.id, score=1.0)],
            total=1,
        )

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"query": {}},
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "record": {
                        "id": str(record.id),
                        "status": RecordStatus.pending,
                        "fields": record.fields,
                        "metadata": record.metadata_,
                        "external_id": record.external_id,
                        "dataset_id": str(dataset.id),
                        "inserted_at": record.inserted_at.isoformat(),
                        "updated_at": record.updated_at.isoformat(),
                    },
                    "query_score": 1.0,
                }
            ],
            "total": 1,
        }

    async def test_search_with_filtered_metadata_as_annotator(
        self,
        async_client: AsyncClient,
        mock_search_engine: SearchEngine,
    ):
        user = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create()
        await WorkspaceUserFactory.create(user_id=user.id, workspace_id=dataset.workspace_id)

        await TextFieldFactory.create(name="input", dataset=dataset)
        await TermsMetadataPropertyFactory.create(
            name="annotator_meta", dataset=dataset, allowed_roles=[UserRole.admin, UserRole.annotator]
        )
        await TermsMetadataPropertyFactory.create(name="admin_meta", dataset=dataset, allowed_roles=[UserRole.admin])
        await TermsMetadataPropertyFactory.create(name="owner_meta", dataset=dataset, allowed_roles=[])

        record = await RecordFactory.create(
            metadata_={"admin_meta": "value", "annotator_meta": "value", "owner_meta": "value", "extra": "value"},
            dataset=dataset,
        )

        mock_search_engine.search.return_value = SearchResponses(
            items=[SearchResponseItem(record_id=record.id, score=1.0)],
            total=1,
        )

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"query": {}},
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "record": {
                        "id": str(record.id),
                        "status": RecordStatus.pending,
                        "fields": record.fields,
                        "metadata": {"annotator_meta": "value"},
                        "external_id": record.external_id,
                        "dataset_id": str(dataset.id),
                        "inserted_at": record.inserted_at.isoformat(),
                        "updated_at": record.updated_at.isoformat(),
                    },
                    "query_score": 1.0,
                }
            ],
            "total": 1,
        }

    async def test_search_with_filtered_metadata_as_admin(
        self,
        async_client: AsyncClient,
        mock_search_engine: SearchEngine,
    ):
        dataset = await DatasetFactory.create()

        user = await AdminFactory.create()
        await WorkspaceUserFactory.create(user_id=user.id, workspace_id=dataset.workspace_id)

        await TextFieldFactory.create(name="input", dataset=dataset)
        await TermsMetadataPropertyFactory.create(
            name="annotator_meta", dataset=dataset, allowed_roles=[UserRole.admin, UserRole.annotator]
        )
        await TermsMetadataPropertyFactory.create(name="admin_meta", dataset=dataset, allowed_roles=[UserRole.admin])
        await TermsMetadataPropertyFactory.create(name="owner_meta", dataset=dataset, allowed_roles=[])
        record = await RecordFactory.create(
            metadata_={"admin_meta": "value", "annotator_meta": "value", "owner_meta": "value", "extra": "value"},
            dataset=dataset,
        )

        mock_search_engine.search.return_value = SearchResponses(
            items=[SearchResponseItem(record_id=record.id, score=1.0)],
            total=1,
        )

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"query": {}},
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "record": {
                        "id": str(record.id),
                        "status": RecordStatus.pending,
                        "fields": record.fields,
                        "metadata": {"admin_meta": "value", "annotator_meta": "value", "extra": "value"},
                        "external_id": record.external_id,
                        "dataset_id": str(dataset.id),
                        "inserted_at": record.inserted_at.isoformat(),
                        "updated_at": record.updated_at.isoformat(),
                    },
                    "query_score": 1.0,
                }
            ],
            "total": 1,
        }

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

    async def test_with_invalid_filter(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "query": {
                    "text": {"q": "text", "field": "non-existent"},
                },
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
            "detail": f"Question not found filtering by name=non-existent, dataset_id={dataset.id}",
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
