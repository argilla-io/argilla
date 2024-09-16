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

from datetime import datetime
from typing import List

from rq.job import Job
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.webhooks.v1.enums import RecordEvent
from argilla_server.webhooks.v1.schemas import RecordEventSchema
from argilla_server.jobs.webhook_jobs import enqueue_notify_events
from argilla_server.models import Record, Dataset


async def notify_record_event(db: AsyncSession, record_event: RecordEvent, record: Record) -> List[Job]:
    if record_event == RecordEvent.deleted:
        return await _notify_record_deleted_event(db, record)

    (
        await db.execute(
            select(Dataset)
            .where(Dataset.id == record.dataset_id)
            .options(
                selectinload(Dataset.workspace),
                selectinload(Dataset.fields),
                selectinload(Dataset.questions),
                selectinload(Dataset.metadata_properties),
                selectinload(Dataset.vectors_settings),
            )
        )
    ).scalar_one()

    return await enqueue_notify_events(
        db,
        event=record_event,
        timestamp=datetime.utcnow(),
        data=RecordEventSchema.from_orm(record).dict(),
    )


async def _notify_record_deleted_event(db: AsyncSession, record: Record) -> List[Job]:
    return await enqueue_notify_events(
        db,
        event=RecordEvent.deleted,
        timestamp=datetime.utcnow(),
        data={"id": record.id},
    )
