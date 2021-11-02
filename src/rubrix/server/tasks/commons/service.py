from fastapi import Depends

from rubrix.server.datasets.service import DatasetsService
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao


class TaskService:

    _INSTANCE = None

    def __init__(self, datasets: DatasetsService, dao: DatasetRecordsDAO):
        self.__datasets__ = datasets
        self.__dao__ = dao

    @classmethod
    def get_instance(
        cls,
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        dao: DatasetRecordsDAO = Depends(dataset_records_dao),
    ) -> "TaskService":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(datasets, dao=dao)
        return cls._INSTANCE
