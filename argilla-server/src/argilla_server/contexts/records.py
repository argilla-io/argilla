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

from typing import Dict, Sequence, Union, List, Tuple
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from argilla_server.database import get_async_db
from argilla_server.models import Dataset, Record, VectorSettings, Vector


async def list_records_by_dataset_id(
    dataset_id: UUID,
    offset: int,
    limit: int,
    with_responses: bool = False,
    with_suggestions: bool = False,
    with_vectors: Union[bool, List[str]] = False,
) -> Tuple[Sequence[Record], int]:
    query = Record.Select.by_dataset_id(
        dataset_id=dataset_id,
        offset=offset,
        limit=limit,
        with_responses=with_responses,
        with_suggestions=with_suggestions,
        with_vectors=with_vectors,
    )

    async for db in get_async_db():
        records = (await db.scalars(query)).unique().all()
        total = await db.scalar(Record.Select.count(dataset_id=dataset_id))

        return records, total


async def list_dataset_records_by_ids(
    db: AsyncSession, dataset_id: UUID, record_ids: Sequence[UUID]
) -> Sequence[Record]:
    query = Record.Select.by_dataset_id(dataset_id=dataset_id).where(Record.id.in_(record_ids))
    return (await db.scalars(query)).unique().all()


async def list_dataset_records_by_external_ids(
    db: AsyncSession, dataset_id: UUID, external_ids: Sequence[str]
) -> Sequence[Record]:
    query = (
        Record.Select.by_dataset_id(dataset_id=dataset_id)
        .where(Record.external_id.in_(external_ids))
        .options(selectinload(Record.dataset))
    )

    return (await db.scalars(query)).unique().all()


async def fetch_records_by_ids_as_dict(
    db: AsyncSession, dataset: Dataset, record_ids: Sequence[UUID]
) -> Dict[UUID, Record]:
    records_by_ids = await list_dataset_records_by_ids(db, dataset.id, record_ids)
    return {record.id: record for record in records_by_ids}


async def fetch_records_by_external_ids_as_dict(
    db: AsyncSession, dataset: Dataset, external_ids: Sequence[str]
) -> Dict[str, Record]:
    records_by_external_ids = await list_dataset_records_by_external_ids(db, dataset.id, external_ids)
    return {record.external_id: record for record in records_by_external_ids}
