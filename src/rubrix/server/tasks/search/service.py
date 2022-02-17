import logging
from typing import Iterable, List, Optional, Set, Type

from fastapi import Depends

from rubrix.server.commons.es_helpers import sort_by2elasticsearch
from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons import BaseRecord, EsRecordDataFieldNames
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.search.model import BaseSearchQuery, SearchResults, SortConfig


class SearchRecordsService:
    """Generic service for search records operations"""

    def __init__(self, dao: DatasetRecordsDAO, metrics: MetricsService):
        self.__dao__ = dao
        self.__metrics__ = metrics

    __LOGGER__ = logging.getLogger(__name__)

    @classmethod
    def get_instance(
        cls,
        dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ):
        return cls(dao=dao, metrics=metrics)

    def search(
        self,
        dataset: Dataset,
        query: BaseSearchQuery,
        sort_config: SortConfig,
        record_type: Type[BaseRecord],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
        metrics: Optional[Set[str]] = None,
    ) -> SearchResults:

        if record_from > 0:
            metrics = None

        exclude_fields = ["metrics.*"] if exclude_metrics else None
        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(
                # TODO: This must be hidden inside dao implementation
                query=query.as_elasticsearch(),
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
                include_default_aggregations=False,
            ),
            size=size,
            record_from=record_from,
            exclude_fields=exclude_fields,
        )
        metrics_results = {}
        for metric_id in metrics or []:
            try:
                metrics = self.__metrics__.summarize_metric(
                    dataset=dataset, metric=metric_id, query=query
                )
                metrics_results[metric_id] = metrics
            except Exception as ex:
                self.__LOGGER__.warning(
                    "Cannot compute metric [%s]. Error: %s", metric_id, ex
                )
                metrics_results[metric_id] = {}

        return SearchResults(
            total=results.total,
            records=[record_type.parse_obj(r) for r in results.records],
            metrics=metrics_results if metrics_results else {},
        )
