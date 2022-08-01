from typing import List, Optional, Type

from fastapi import Depends

from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.services.datasets import ServiceDataset
from rubrix.server.services.metrics.models import ServiceBaseTaskMetrics, ServiceMetric
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

    def store_records(
        self,
        dataset: ServiceDataset,
        records: List[ServiceRecord],
        record_type: Type[ServiceRecord],
        metrics: Optional[Type[ServiceBaseTaskMetrics]] = None,
    ) -> int:
        """Store a set of records"""
        if metrics:
            for record in records:
                record.metrics = metrics.record_metrics(record)

        return self.__dao__.add_records(
            dataset=dataset,
            records=records,
            record_class=record_type,
        )
