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
from httpx import AsyncClient

from tests.factories import DatasetFactory, RecordFactory, TextFieldFactory, VectorFactory, VectorSettingsFactory


@pytest.mark.asyncio
class TestSearchCurrentUserDatasetRecords:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/me/datasets/{dataset_id}/records/search"

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
            "detail": f"Record `{record_without_vector.id}` does not have a vector for vector settings `{vector_settings.name}`"
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
            "detail": f"Question with name `non-existent` not found for dataset with id `{dataset.id}`"
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
            "detail": f"Question with name `non-existent` not found for dataset with id `{dataset.id}`"
        }
