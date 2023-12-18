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

from typing import AsyncGenerator
from uuid import UUID

from argilla.server.database import AsyncSessionLocal
from argilla.server.jobs.queues import default_queue
from argilla.server.models import Dataset, Record, Response, Suggestion
from argilla.server.search_engine import SearchEngine, get_search_engine
from rq import Retry
from rq.decorators import job
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


# TODO: Once we merge the branch with reindex cli task we can remove this class and use the other one.
class Reindexer:
    YIELD_PER = 100

    @classmethod
    async def reindex_dataset(cls, db: AsyncSession, search_engine: SearchEngine, dataset_id: UUID) -> Dataset:
        dataset = (
            await db.execute(
                select(Dataset)
                .filter_by(id=dataset_id)
                .options(
                    selectinload(Dataset.fields),
                    selectinload(Dataset.questions),
                    selectinload(Dataset.metadata_properties),
                    selectinload(Dataset.vectors_settings),
                )
            )
        ).scalar_one()

        await search_engine.delete_index(dataset)
        await search_engine.create_index(dataset)

        return dataset

    @classmethod
    async def reindex_dataset_records(
        cls, db: AsyncSession, search_engine: SearchEngine, dataset: Dataset
    ) -> AsyncGenerator[list[Record], None]:
        stream = await db.stream(
            select(Record)
            .filter_by(dataset_id=dataset.id)
            .order_by(Record.inserted_at.asc())
            .options(
                selectinload(Record.responses).selectinload(Response.user),
                selectinload(Record.suggestions).selectinload(Suggestion.question),
                selectinload(Record.vectors),
            )
            .execution_options(yield_per=cls.YIELD_PER)
        )

        async for records_partition in stream.partitions():
            records = [record for (record,) in records_partition]

            await search_engine.index_records(dataset, records)

            yield records


# NOTE:
# This could be executed as a normal function:
# > await reindex_dataset(UUID("cfcc028a-1669-4b6a-baf5-9b50e0538e44"))
# Or with rq in background:
# > reindex_dataset.delay(UUID("cfcc028a-1669-4b6a-baf5-9b50e0538e44"))
@job(default_queue, retry=Retry(max=3, interval=60))
async def reindex_dataset(dataset_id: UUID):
    async with AsyncSessionLocal() as db:
        async for search_engine in get_search_engine():
            dataset = await Reindexer.reindex_dataset(db, search_engine, dataset_id)

            async for records in Reindexer.reindex_dataset_records(db, search_engine, dataset):
                ...
