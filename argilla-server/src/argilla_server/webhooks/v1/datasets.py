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
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import Dataset
from argilla_server.webhooks.v1.event import Event
from argilla_server.webhooks.v1.schemas import DatasetEventSchema
from argilla_server.webhooks.v1.enums import DatasetEvent


async def notify_dataset_event(db: AsyncSession, dataset_event: DatasetEvent, dataset: Dataset) -> List[Job]:
    event = await build_dataset_event(db, dataset_event, dataset)

    return await event.notify(db)


async def build_dataset_event(db: AsyncSession, dataset_event: DatasetEvent, dataset: Dataset) -> Event:
    # NOTE: Force loading required association resources required by the event schema
    (
        await db.execute(
            select(Dataset)
            .where(Dataset.id == dataset.id)
            .options(
                selectinload(Dataset.workspace),
                selectinload(Dataset.questions),
                selectinload(Dataset.fields),
                selectinload(Dataset.metadata_properties),
                selectinload(Dataset.vectors_settings),
            )
        )
    ).scalar_one()

    return Event(
        event=dataset_event,
        timestamp=datetime.utcnow(),
        data=DatasetEventSchema.model_validate(dataset).model_dump(),
    )
