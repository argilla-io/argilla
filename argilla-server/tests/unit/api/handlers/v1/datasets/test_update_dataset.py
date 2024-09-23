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

from argilla_server.enums import DatasetDistributionStrategy, DatasetStatus
from tests.factories import DatasetFactory, RecordFactory, ResponseFactory


@pytest.mark.asyncio
class TestUpdateDataset:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}"

    async def test_update_dataset_distribution(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "distribution": {
                    "strategy": DatasetDistributionStrategy.overlap,
                    "min_submitted": 4,
                },
            },
        )

        assert response.status_code == 200
        assert response.json()["distribution"] == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 4,
        }

        assert dataset.distribution == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 4,
        }

    async def test_update_dataset_without_distribution(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"name": "Dataset updated name"},
        )

        assert response.status_code == 200
        assert response.json()["distribution"] == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 1,
        }

        assert dataset.name == "Dataset updated name"
        assert dataset.distribution == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 1,
        }

    async def test_update_dataset_without_distribution_for_published_dataset(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        response = await async_client.patch(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"name": "Dataset updated name"},
        )

        assert response.status_code == 200
        assert response.json()["distribution"] == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 1,
        }

        assert dataset.name == "Dataset updated name"
        assert dataset.distribution == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 1,
        }

    async def test_update_dataset_distribution_with_invalid_strategy(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "distribution": {
                    "strategy": "invalid_strategy",
                },
            },
        )

        assert response.status_code == 422
        assert dataset.distribution == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 1,
        }

    async def test_update_dataset_distribution_with_invalid_min_submitted_value(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "distribution": {
                    "strategy": DatasetDistributionStrategy.overlap,
                    "min_submitted": 0,
                },
            },
        )

        assert response.status_code == 422
        assert dataset.distribution == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 1,
        }

    async def test_update_dataset_distribution_as_none(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"distribution": None},
        )

        assert response.status_code == 422
        assert dataset.distribution == {
            "strategy": DatasetDistributionStrategy.overlap,
            "min_submitted": 1,
        }
