from typing import Any, Dict, List, Optional, Type

from fastapi import Depends

from rubrix.server.apis.v0.models.commons.model import Record
from rubrix.server.apis.v0.models.datasets import BaseDatasetDB
from rubrix.server.apis.v0.models.metrics.base import BaseTaskMetrics
from rubrix.server.daos.records import DatasetRecordsDAO


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
        dataset: BaseDatasetDB,
        mappings: Dict[str, Any],
        records: List[Record],
        record_type: Type[Record],
        metrics: Optional[Type[BaseTaskMetrics]] = None,
    ) -> int:
        """Store a set of records"""
        if metrics:
            for record in records:
                record.metrics = metrics.record_metrics(record)

        return self.__dao__.add_records(
            dataset=dataset,
            mappings=mappings,
            records=records,
            record_class=record_type,
        )
