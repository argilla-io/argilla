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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from argilla_server.models import Record, Response
from argilla_server.enums import DatasetDistributionStrategy, RecordStatus, ResponseStatus


async def refresh_record_status(db: AsyncSession, record: Record, autocommit: bool) -> Record:
    if record.dataset.distribution_strategy == DatasetDistributionStrategy.overlap:
        return await _refresh_record_status_with_overlap_strategy(db, record, autocommit)

    raise NotImplementedError(f"unsupported distribution strategy `{record.dataset.distribution_strategy}`")


async def _refresh_record_status_with_overlap_strategy(db: AsyncSession, record: Record, autocommit: bool) -> Record:
    count_record_submitted_responses = (
        await db.execute(
            select(func.count(Response.id)).filter_by(status=ResponseStatus.submitted, record_id=record.id)
        )
    ).scalar_one()

    if count_record_submitted_responses >= record.dataset.distribution["min_submitted"]:
        record.status = RecordStatus.completed
    else:
        record.status = RecordStatus.pending

    return await record.save(db, autocommit)
