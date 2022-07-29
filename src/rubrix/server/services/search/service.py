import logging
from typing import Iterable, List, Optional, Type, TypeVar

from fastapi import Depends

from rubrix.server.daos.models.records import RecordSearch
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.elasticseach.query_helpers import sort_by2elasticsearch
from rubrix.server.services.datasets import Dataset
from rubrix.server.services.metrics import BaseMetric, MetricsService
from rubrix.server.services.search.model import (
    BaseSVCSearchQuery,
    Record,
    SearchResults,
    SortConfig,
)
from rubrix.server.services.tasks.commons.record import (
    BaseRecordDB,
    EsRecordDataFieldNames,
)

SvcSearchQuery = TypeVar("SvcSearchQuery", bound=BaseSVCSearchQuery)


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
        dataset: Dataset,
        record_type: Type[BaseRecordDB],
        query: Optional[SvcSearchQuery] = None,
        sort_config: Optional[SortConfig] = None,
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
        metrics: Optional[List[BaseMetric]] = None,
    ) -> SearchResults:

        if record_from > 0:
            metrics = None

        sort_config = sort_config or SortConfig()
        exclude_fields = ["metrics.*"] if exclude_metrics else None
        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(
                query=query,
                # TODO(@frascuchon): sort must be parsed inside de dao
                sort=sort_by2elasticsearch(
                    sort_config.sort_by,
                    valid_fields=[
                        "metadata",
                        EsRecordDataFieldNames.last_updated,
                        EsRecordDataFieldNames.score,
                        EsRecordDataFieldNames.predicted,
                        EsRecordDataFieldNames.predicted_as,
                        EsRecordDataFieldNames.predicted_by,
                        EsRecordDataFieldNames.annotated_as,
                        EsRecordDataFieldNames.annotated_by,
                        EsRecordDataFieldNames.status,
                        EsRecordDataFieldNames.event_timestamp,
                    ],
                ),
            ),
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
        dataset: Dataset,
        record_type: Type[BaseRecordDB],
        query: Optional[SvcSearchQuery] = None,
    ) -> Iterable[Record]:
        """Scan records for a queried"""
        for doc in self.__dao__.scan_dataset(dataset, search=RecordSearch(query=query)):
            yield record_type.parse_obj(doc)
