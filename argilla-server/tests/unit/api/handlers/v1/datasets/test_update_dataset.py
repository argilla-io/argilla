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

import pytest

from uuid import UUID
from httpx import AsyncClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.jobs.queues import HIGH_QUEUE
from argilla_server.enums import DatasetDistributionStrategy, DatasetStatus
from argilla_server.webhooks.v1.datasets import build_dataset_event
from argilla_server.webhooks.v1.enums import DatasetEvent

from tests.factories import DatasetFactory, RecordFactory, ResponseFactory, WebhookFactory


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

    async def test_update_dataset_enqueue_webhook_dataset_updated_event(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        webhook = await WebhookFactory.create(events=[DatasetEvent.updated])

        response = await async_client.patch(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"name": "Updated dataset"},
        )

        assert response.status_code == 200

        event = await build_dataset_event(db, DatasetEvent.updated, dataset)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == DatasetEvent.updated
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)
