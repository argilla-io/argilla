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

import backoff
import sqlalchemy

from typing import List
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.enums import DatasetDistributionStrategy, RecordStatus
from argilla_server.models import Record
from argilla_server.search_engine.base import SearchEngine
from argilla_server.database import _get_async_db

MAX_TIME_RETRY_SQLALCHEMY_ERROR = 15


async def unsafe_update_records_status(db: AsyncSession, records: List[Record]):
    for record in records:
        await _update_record_status(db, record)


@backoff.on_exception(backoff.expo, sqlalchemy.exc.SQLAlchemyError, max_time=MAX_TIME_RETRY_SQLALCHEMY_ERROR)
async def update_record_status(search_engine: SearchEngine, record_id: UUID) -> Record:
    async for db in _get_async_db(isolation_level="SERIALIZABLE"):
        record = await Record.get_or_raise(
            db,
            record_id,
            options=[
                selectinload(Record.dataset),
                selectinload(Record.responses_submitted),
            ],
        )

        await _update_record_status(db, record)
        await search_engine.partial_record_update(record, status=record.status)

        await db.commit()

        return record


async def _update_record_status(db: AsyncSession, record: Record) -> Record:
    if record.dataset.distribution_strategy == DatasetDistributionStrategy.overlap:
        return await _update_record_status_with_overlap_strategy(db, record)

    raise NotImplementedError(f"unsupported distribution strategy `{record.dataset.distribution_strategy}`")


async def _update_record_status_with_overlap_strategy(db: AsyncSession, record: Record) -> Record:
    if len(record.responses_submitted) >= record.dataset.distribution["min_submitted"]:
        record.status = RecordStatus.completed
    else:
        record.status = RecordStatus.pending

    return await record.save(db, autocommit=False)
