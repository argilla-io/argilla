from typing import List, Type

from fastapi import Depends

from rubrix.server.datasets.model import BaseDatasetDB
from rubrix.server.tasks.commons import BaseRecord, Record, TaskType
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO
from rubrix.server.tasks.commons.task_factory import TaskFactory


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

        for task in [
            TaskType.text2text,
            TaskType.text_classification,
            TaskType.token_classification,
        ]:
            self.__dao__.register_task_mappings(
                task, TaskFactory.get_task_mappings(task)
            )

    def store_records(
        self,
        dataset: BaseDatasetDB,
        records: List[Record],
        record_type: Type[Record],
    ) -> int:
        """Store a set of records"""
        self._compute_record_metrics(dataset, records)
        return self.__dao__.add_records(
            dataset=dataset,
            records=records,
            record_class=record_type,
        )

    def _compute_record_metrics(self, dataset: BaseDatasetDB, records: List[Record]):
        """Computes metrics for each record"""
        metrics = TaskFactory.get_task_metrics(dataset.task)
        if metrics:
            for record in records:
                record.metrics = metrics.record_metrics(record)
