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

from argilla_server.models import User
from argilla_server.jobs.queues import HIGH_QUEUE
from argilla_server.webhooks.v1.enums import RecordEvent, ResponseEvent
from argilla_server.webhooks.v1.responses import build_response_event
from argilla_server.webhooks.v1.records import build_record_event
from argilla_server.enums import DatasetDistributionStrategy, RecordStatus, ResponseStatus

from tests.factories import DatasetFactory, RecordFactory, ResponseFactory, TextQuestionFactory, WebhookFactory


@pytest.mark.asyncio
class TestDeleteResponse:
    def url(self, response_id: UUID) -> str:
        return f"/api/v1/responses/{response_id}"

    async def test_delete_response_updates_record_status_to_pending(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            }
        )

        record = await RecordFactory.create(status=RecordStatus.completed, dataset=dataset)
        response = await ResponseFactory.create(record=record)

        resp = await async_client.delete(self.url(response.id), headers=owner_auth_header)

        assert resp.status_code == 200
        assert record.status == RecordStatus.pending

    async def test_delete_response_does_not_updates_record_status_to_pending(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            }
        )

        record = await RecordFactory.create(status=RecordStatus.completed, dataset=dataset)
        responses = await ResponseFactory.create_batch(3, record=record)

        resp = await async_client.delete(self.url(responses[0].id), headers=owner_auth_header)

        assert resp.status_code == 200
        assert record.status == RecordStatus.completed

    async def test_delete_response_enqueue_webhook_response_deleted_event(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await ResponseFactory.create()
        webhook = await WebhookFactory.create(events=[ResponseEvent.deleted])

        event = await build_response_event(db, ResponseEvent.deleted, response)

        resp = await async_client.delete(self.url(response.id), headers=owner_auth_header)

        assert resp.status_code == 200

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == ResponseEvent.deleted
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)

    async def test_delete_response_enqueue_webhook_record_updated_event(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        record = await RecordFactory.create()
        responses = await ResponseFactory.create_batch(2, record=record)
        webhook = await WebhookFactory.create(events=[RecordEvent.updated])

        response = await async_client.delete(self.url(responses[0].id), headers=owner_auth_header)

        assert response.status_code == 200

        event = await build_record_event(db, RecordEvent.updated, record)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.updated
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)

    async def test_delete_response_enqueue_webhook_record_completed_event(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        record = await RecordFactory.create()
        responses = await ResponseFactory.create_batch(2, record=record)
        webhook = await WebhookFactory.create(events=[RecordEvent.completed])

        response = await async_client.delete(self.url(responses[0].id), headers=owner_auth_header)

        assert response.status_code == 200

        event = await build_record_event(db, RecordEvent.completed, record)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.completed
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)
