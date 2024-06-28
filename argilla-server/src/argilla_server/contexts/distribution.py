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

from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.enums import DatasetDistributionStrategy, RecordStatus
from argilla_server.models import Record


# TODO: Do this with one single update statement for all records if possible to avoid too many queries.
async def update_records_status(db: AsyncSession, records: List[Record], autocommit: bool):
    for record in records:
        await update_record_status(db, record, autocommit)


async def update_record_status(db: AsyncSession, record: Record, autocommit: bool) -> Record:
    if record.dataset.distribution_strategy == DatasetDistributionStrategy.overlap:
        return await _update_record_status_with_overlap_strategy(db, record, autocommit)

    raise NotImplementedError(f"unsupported distribution strategy `{record.dataset.distribution_strategy}`")


async def _update_record_status_with_overlap_strategy(db: AsyncSession, record: Record, autocommit: bool) -> Record:
    if len(record.submitted_responses) >= record.dataset.distribution["min_submitted"]:
        record.status = RecordStatus.completed
    else:
        record.status = RecordStatus.pending

    return await record.save(db, autocommit)
