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

from argilla_server.models import Response, Record, Dataset
from argilla_server.webhooks.v1.event import Event
from argilla_server.webhooks.v1.enums import ResponseEvent
from argilla_server.webhooks.v1.schemas import ResponseEventSchema


async def notify_response_event(db: AsyncSession, response_event: ResponseEvent, response: Response) -> List[Job]:
    event = await build_response_event(db, response_event, response)

    return await event.notify(db)


async def build_response_event(db: AsyncSession, response_event: ResponseEvent, response: Response) -> Event:
    # NOTE: Force loading required association resources required by the event schema
    (
        await db.execute(
            select(Response)
            .where(Response.id == response.id)
            .options(
                selectinload(Response.user),
                selectinload(Response.record).options(
                    selectinload(Record.dataset).options(
                        selectinload(Dataset.workspace),
                        selectinload(Dataset.questions),
                        selectinload(Dataset.fields),
                        selectinload(Dataset.metadata_properties),
                        selectinload(Dataset.vectors_settings),
                    ),
                ),
            ),
        )
    ).scalar_one()

    return Event(
        event=response_event,
        timestamp=datetime.utcnow(),
        data=ResponseEventSchema.model_validate(response).model_dump(),
    )
