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

from typing import List, Type

from fastapi import Depends

from rubrix.server.commons import telemetry
from rubrix.server.commons.config import TasksFactory
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.services.datasets import ServiceDataset
from rubrix.server.services.tasks.commons import ServiceRecord


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
