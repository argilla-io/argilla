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

from rq import Retry
from rq.decorators import job

from sqlalchemy import func, select

from argilla_server.models import Record, Response
from argilla_server.database import AsyncSessionLocal
from argilla_server.jobs.queues import DEFAULT_QUEUE
from argilla_server.search_engine.base import SearchEngine
from argilla_server.settings import settings
from argilla_server.contexts import distribution

JOB_TIMEOUT_DISABLED = -1
JOB_RECORDS_YIELD_PER = 100


@job(DEFAULT_QUEUE, timeout=JOB_TIMEOUT_DISABLED, retry=Retry(max=3))
async def update_dataset_records_status_job(dataset_id: UUID) -> None:
    """This Job updates the status of all the records in the dataset when the distribution strategy changes."""

    record_ids = []

    async with AsyncSessionLocal() as db:
        stream = await db.stream(
            select(Record.id)
            .join(Response)
            .where(Record.dataset_id == dataset_id)
            .order_by(Record.inserted_at.asc())
            .execution_options(yield_per=JOB_RECORDS_YIELD_PER)
        )

        async for record_id in stream.scalars():
            record_ids.append(record_id)

    # NOTE: We are updating the records status outside the database transaction to avoid database locks with SQLite.
    async with SearchEngine.get_by_name(settings.search_engine) as search_engine:
        for record_id in record_ids:
            await distribution.update_record_status(search_engine, record_id)
