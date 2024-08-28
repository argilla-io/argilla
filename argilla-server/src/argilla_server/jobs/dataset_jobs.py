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

from argilla_server.models import Record
from argilla_server.database import AsyncSessionLocal
from argilla_server.jobs.queues import default_queue
from argilla_server.search_engine.base import SearchEngine
from argilla_server.settings import settings
from argilla_server.contexts import distribution

YIELD_PER = 100


@job(default_queue, retry=Retry(max=3))
async def update_dataset_records_status_job(dataset_id: UUID):
    """This Job worker updates the status of all the records in the dataset when the distribution strategy changes."""

    async with AsyncSessionLocal() as db, SearchEngine.get_by_name(settings.search_engine) as search_engine:
        stream = await db.stream(
            select(Record.id)
            .where(Record.dataset_id == dataset_id)
            .order_by(Record.inserted_at.asc())
            .execution_options(yield_per=YIELD_PER)
        )

        # NOTE: Avoiding this previous implementation to avoid big transactions and instead enqueuing a job for each record
        # async for record_id in stream.scalars():
        #     await distribution.update_record_status(search_engine, record_id)

        async for record_id in stream.scalars():
            update_record_status_job.delay(record_id)


@job(default_queue, retry=Retry(max=3))
async def update_record_status_job(record_id: UUID):
    async with SearchEngine.get_by_name(settings.search_engine) as search_engine:
        await distribution.update_record_status(search_engine, record_id)
