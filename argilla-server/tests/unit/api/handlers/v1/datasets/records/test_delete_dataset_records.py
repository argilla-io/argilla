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
from argilla_server.webhooks.v1.enums import RecordEvent
from argilla_server.webhooks.v1.records import build_record_event

from tests.factories import DatasetFactory, RecordFactory, WebhookFactory


@pytest.mark.asyncio
class TestDeleteDatasetRecords:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records"

    async def test_delete_dataset_records_enqueue_webhook_record_deleted_events(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        records = await RecordFactory.create_batch(2, dataset=dataset)
        webhook = await WebhookFactory.create(events=[RecordEvent.deleted])

        event_a = await build_record_event(db, RecordEvent.deleted, records[0])
        event_b = await build_record_event(db, RecordEvent.deleted, records[1])

        response = await async_client.delete(
            self.url(dataset.id),
            headers=owner_auth_header,
            params={"ids": f"{records[0].id},{records[1].id}"},
        )

        assert response.status_code == 204

        assert HIGH_QUEUE.count == 2

        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.deleted
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event_a.data)

        assert HIGH_QUEUE.jobs[1].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[1].args[1] == RecordEvent.deleted
        assert HIGH_QUEUE.jobs[1].args[3] == jsonable_encoder(event_b.data)
