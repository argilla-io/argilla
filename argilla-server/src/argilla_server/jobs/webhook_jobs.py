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

import httpx

from typing import List

from uuid import UUID
from datetime import datetime

from rq.job import Retry, Job
from rq.decorators import job
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from argilla_server.webhooks.v1.commons import notify_event
from argilla_server.database import AsyncSessionLocal
from argilla_server.jobs.queues import HIGH_QUEUE
from argilla_server.contexts import webhooks
from argilla_server.models import Webhook


async def enqueue_notify_events(db: AsyncSession, event: str, timestamp: datetime, data: dict) -> List[Job]:
    enabled_webhooks = await webhooks.list_enabled_webhooks(db)
    if len(enabled_webhooks) == 0:
        return []

    enqueued_jobs = []
    jsonable_data = jsonable_encoder(data)
    for enabled_webhook in enabled_webhooks:
        if event in enabled_webhook.events:
            enqueue_job = notify_event_job.delay(enabled_webhook.id, event, timestamp, jsonable_data)
            enqueued_jobs.append(enqueue_job)

    return enqueued_jobs


@job(HIGH_QUEUE, retry=Retry(max=3, interval=[10, 60, 180]))
async def notify_event_job(webhook_id: UUID, event: str, timestamp: datetime, data: dict) -> None:
    async with AsyncSessionLocal() as db:
        webhook = await Webhook.get_or_raise(db, webhook_id)

    response = notify_event(webhook, event, timestamp, data)
    response.raise_for_status()
