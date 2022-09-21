import dataclasses
from typing import List, Optional, Type

from fastapi import Depends

from rubrix.server.commons import telemetry
from rubrix.server.commons.config import TasksFactory
from rubrix.server.commons.models import TaskStatus
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.errors import ForbiddenOperationError
from rubrix.server.security.model import User
from rubrix.server.services.datasets import ServiceDataset
from rubrix.server.services.search.model import ServiceBaseRecordsQuery
from rubrix.server.services.tasks.commons import ServiceRecord


@dataclasses.dataclass
class DeleteRecordsOut:
    processed: int
    discarded: Optional[int] = None
    deleted: Optional[int] = None


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
            processed=processed,
            discarded=discarded,
            deleted=deleted,
        )
