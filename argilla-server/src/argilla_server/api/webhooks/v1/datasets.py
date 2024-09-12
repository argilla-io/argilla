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

from typing import List
from datetime import datetime

from rq.job import Job
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import Dataset
from argilla_server.jobs.webhook_jobs import enqueue_notify_events
from argilla_server.api.webhooks.v1.schemas import DatasetEventSchema
from argilla_server.api.webhooks.v1.enums import DatasetEvent


async def notify_dataset_event(db: AsyncSession, dataset_event: DatasetEvent, dataset: Dataset) -> List[Job]:
    if dataset_event == DatasetEvent.deleted:
        return await _notify_dataset_deleted_event(db, dataset)

    # NOTE: Not using selectinload or other eager loading strategies here to
    # avoid replacing the current state of the resource that we want to notify.
    await dataset.awaitable_attrs.workspace
    await dataset.awaitable_attrs.questions
    await dataset.awaitable_attrs.fields
    await dataset.awaitable_attrs.metadata_properties
    await dataset.awaitable_attrs.vectors_settings

    return await enqueue_notify_events(
        db,
        event=dataset_event,
        timestamp=datetime.utcnow(),
        data=DatasetEventSchema.from_orm(dataset).dict(),
    )


async def _notify_dataset_deleted_event(db: AsyncSession, dataset: Dataset) -> List[Job]:
    return await enqueue_notify_events(
        db,
        event=DatasetEvent.deleted,
        timestamp=datetime.utcnow(),
        data={"id": dataset.id},
    )
