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

import dataclasses
from typing import List, Optional, Type

from fastapi import Depends

from argilla.server.commons import telemetry
from argilla.server.commons.config import TasksFactory
from argilla.server.commons.models import TaskStatus
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.errors import ForbiddenOperationError
from argilla.server.security.model import User
from argilla.server.services.datasets import ServiceDataset
from argilla.server.services.search.model import ServiceBaseRecordsQuery
from argilla.server.services.tasks.commons import ServiceRecord


@dataclasses.dataclass
class DeleteRecordsOut:
    processed: int = 0
    discarded: int = 0
    deleted: int = 0


class RecordsStorageService:

    _INSTANCE: "RecordsStorageService" = None

    @classmethod
    def get_instance(
        cls,
        dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
    ) -> "RecordsStorageService":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetRecordsDAO):
        self.__dao__ = dao

    async def store_records(
        self,
        dataset: ServiceDataset,
        records: List[ServiceRecord],
        record_type: Type[ServiceRecord],
    ) -> int:
        """Store a set of records"""
        await telemetry.track_bulk(task=dataset.task, records=len(records))

        metrics = TasksFactory.get_task_metrics(dataset.task)
        if metrics:
            for record in records:
                record.metrics = metrics.record_metrics(record)

        return self.__dao__.add_records(
            dataset=dataset,
            records=records,
            record_class=record_type,
        )

    async def delete_records(
        self,
        user: User,
        dataset: ServiceDataset,
        query: Optional[ServiceBaseRecordsQuery] = None,
        mark_as_discarded: bool = False,
    ) -> DeleteRecordsOut:
        processed, discarded, deleted = None, None, None
        if mark_as_discarded:
            processed, discarded = await self.__dao__.update_records_by_query(
                dataset,
                query=query,
                status=TaskStatus.discarded,
            )
        else:
            if not user.is_superuser() and user.username != dataset.created_by:
                raise ForbiddenOperationError(
                    f"You don't have the necessary permissions to delete records on this dataset. "
                    "Only dataset creators or administrators can delete datasets"
                )

            processed, deleted = await self.__dao__.delete_records_by_query(
                dataset, query=query
            )

        return DeleteRecordsOut(
            processed=processed or 0,
            discarded=discarded or 0,
            deleted=deleted or 0,
        )
