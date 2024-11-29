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

from tests.factories import RecordFactory, WebhookFactory


@pytest.mark.asyncio
class TestUpdateRecord:
    def url(self, record_id: UUID) -> str:
        return f"/api/v1/records/{record_id}"

    async def test_update_record_enqueue_webhook_record_updated_event(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        record = await RecordFactory.create()
        webhook = await WebhookFactory.create(events=[RecordEvent.updated])

        response = await async_client.patch(
            self.url(record.id),
            headers=owner_auth_header,
            json={"metadata": {"new": "value"}},
        )

        assert response.status_code == 200

        event = await build_record_event(db, RecordEvent.updated, record)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.updated
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)
