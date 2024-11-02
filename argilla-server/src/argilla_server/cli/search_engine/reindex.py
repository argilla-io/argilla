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
import asyncio
from typing import AsyncGenerator, Optional
from uuid import UUID

import typer
from rich.progress import Progress
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.cli.rich import echo_in_panel
from argilla_server.database import AsyncSessionLocal
from argilla_server.models import Dataset, Record, Response, Suggestion
from argilla_server.search_engine import SearchEngine, get_search_engine


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
    async def reindex_datasets(cls, db: AsyncSession, search_engine: SearchEngine) -> AsyncGenerator[Dataset, None]:
        stream = await db.stream(
            select(Dataset)
            .order_by(Dataset.inserted_at.asc())
            .options(
                selectinload(Dataset.fields),
                selectinload(Dataset.questions),
                selectinload(Dataset.metadata_properties),
                selectinload(Dataset.vectors_settings),
            )
            .execution_options(yield_per=cls.YIELD_PER)
        )

        async for dataset in stream.scalars():
            await search_engine.delete_index(dataset)
            await search_engine.create_index(dataset)

            yield dataset

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

    @classmethod
    async def count_datasets(cls, db: AsyncSession) -> int:
        return (await db.execute(select(func.count(Dataset.id)))).scalar_one()

    @classmethod
    async def count_dataset_records(cls, db: AsyncSession, dataset: Dataset) -> int:
        return (await db.execute(select(func.count(Record.id)).filter_by(dataset_id=dataset.id))).scalar_one()


async def _reindex_dataset(db: AsyncSession, search_engine: SearchEngine, progress: Progress, dataset_id: UUID) -> None:
    try:
        dataset = await Reindexer.reindex_dataset(db, search_engine, dataset_id)
    except NoResultFound as e:
        echo_in_panel(
            f"Dataset with id={dataset_id} not found.",
            title="Dataset not found",
            title_align="left",
            success=False,
        )

        raise typer.Exit(code=1) from e

    task = progress.add_task(f"reindexing dataset `{dataset.name}`...", total=1)

    await _reindex_dataset_records(db, search_engine, progress, dataset)

    progress.advance(task)


async def _reindex_datasets(db: AsyncSession, search_engine: SearchEngine, progress: Progress) -> None:
    task = progress.add_task("reindexing datasets...", total=await Reindexer.count_datasets(db))

    async for dataset in Reindexer.reindex_datasets(db, search_engine):
        await _reindex_dataset_records(db, search_engine, progress, dataset)

        progress.advance(task)


async def _reindex_dataset_records(
    db: AsyncSession, search_engine: SearchEngine, progress: Progress, dataset: Dataset
) -> None:
    task = progress.add_task(
        f"reindexing dataset `{dataset.name}` records...",
        total=await Reindexer.count_dataset_records(db, dataset),
    )

    async for records in Reindexer.reindex_dataset_records(db, search_engine, dataset):
        progress.advance(task, advance=len(records))


async def _reindex(dataset_id: Optional[UUID] = None) -> None:
    async with AsyncSessionLocal() as db:
        async for search_engine in get_search_engine():
            with Progress() as progress:
                if dataset_id is not None:
                    await _reindex_dataset(db, search_engine, progress, dataset_id)
                else:
                    await _reindex_datasets(db, search_engine, progress)


def reindex(
    dataset_id: Optional[UUID] = typer.Option(None, help="The id of a dataset to be reindexed"),
) -> None:
    asyncio.run(_reindex(dataset_id))


if __name__ == "__main__":
    typer.run(reindex)
