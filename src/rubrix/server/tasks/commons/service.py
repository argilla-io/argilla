from typing import Any, Optional

from fastapi import Depends

from rubrix.server.commons.errors import EntityNotFoundError
from rubrix.server.datasets.service import DatasetsService, create_dataset_service
from rubrix.server.metrics.model import DatasetMetricResults
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch


class TaskService:

    _INSTANCE = None

    def __init__(
        self,
        datasets: DatasetsService,
        dao: DatasetRecordsDAO,
    ):
        self.__datasets__ = datasets
        self.__dao__ = dao

    @classmethod
    def get_instance(
        cls,
        datasets: DatasetsService = Depends(create_dataset_service),
        dao: DatasetRecordsDAO = Depends(dataset_records_dao),
    ) -> "TaskService":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(datasets, dao=dao)
        return cls._INSTANCE

    def calculate_metrics(
        self,
        dataset: str,
        owner: Optional[str],
        metric_id: str,
        query: Any,
    ) -> DatasetMetricResults:
        dataset = self.__datasets__.find_by_name(dataset, owner=owner)

        metric = dataset.get_metric_by_id(metric_id)
        if not metric:
            raise EntityNotFoundError(name=metric_id, type=DatasetMetricResults)

        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(
                query=query.as_elasticsearch() if query else None,
                aggregations={metric.id: metric.spec},
            ),
            size=0,
        )

        for m in results.metrics:
            if metric_id == m.id:
                return m
