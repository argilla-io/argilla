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
from argilla_server.contexts.datasets import CREATE_DATASET_VECTOR_SETTINGS_MAX_COUNT
from httpx import AsyncClient

from tests.factories import DatasetFactory, VectorSettingsFactory


@pytest.mark.asyncio
class TestCreateDatasetVectorSettings:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/vectors-settings"

    async def test_with_maximum_number_of_vector_settings_reached(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await VectorSettingsFactory.create_batch(CREATE_DATASET_VECTOR_SETTINGS_MAX_COUNT, dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "dimensions": 3,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"The maximum number of vector settings has been reached for dataset with id `{dataset.id}`"
        }
