import logging
from typing import Iterable, List, Optional, Type

from fastapi import Depends

from rubrix.server.daos.models.records import RecordSearch
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.services.datasets import ServiceDataset
from rubrix.server.services.metrics import MetricsService
from rubrix.server.services.metrics.models import ServiceMetric
from rubrix.server.services.search.model import (
    SearchResults,
    ServiceRecord,
    ServiceSearchQuery,
    SortConfig,
)
from rubrix.server.services.tasks.commons.record import ServiceBaseRecord


class SearchRecordsService:
    """Generic service for search records operations"""

    _INSTANCE: "SearchRecordsService" = None

    __LOGGER__ = logging.getLogger(__name__)

    @classmethod
    def get_instance(
        cls,
        dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ):
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao=dao, metrics=metrics)
        return cls._INSTANCE

    def __init__(
        self,
        dao: DatasetRecordsDAO,
        metrics: MetricsService,
    ):
        self.__dao__ = dao
        self.__metrics__ = metrics

    def search(
        self,
        dataset: ServiceDataset,
        record_type: Type[ServiceBaseRecord],
        query: Optional[ServiceSearchQuery] = None,
        sort_config: Optional[SortConfig] = None,
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
        metrics: Optional[List[ServiceMetric]] = None,
    ) -> SearchResults:

        if record_from > 0:
            metrics = None

        sort_config = sort_config or SortConfig()
        exclude_fields = ["metrics.*"] if exclude_metrics else None
        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(query=query, sort=sort_config),
            size=size,
            record_from=record_from,
            exclude_fields=exclude_fields,
            highligth_results=query is not None
            and query.query_text is not None
            and len(query.query_text) > 0,
        )
        metrics_results = {}
        for metric in metrics or []:
            try:
                metrics_ = self.__metrics__.summarize_metric(
                    dataset=dataset,
                    metric=metric,
                    record_class=record_type,
                    query=query,
                )
                metrics_results[metric.id] = metrics_
            except Exception as ex:
                self.__LOGGER__.warning(
                    "Cannot compute metric [%s]. Error: %s", metric.id, ex
                )
                metrics_results[metric.id] = {}

        return SearchResults(
            total=results.total,
            records=[record_type.parse_obj(r) for r in results.records],
            metrics=metrics_results if metrics_results else {},
        )

    def scan_records(
        self,
        dataset: ServiceDataset,
        record_type: Type[ServiceBaseRecord],
        query: Optional[ServiceSearchQuery] = None,
    ) -> Iterable[ServiceRecord]:
        """Scan records for a queried"""
        for doc in self.__dao__.scan_dataset(dataset, search=RecordSearch(query=query)):
            yield record_type.parse_obj(doc)
