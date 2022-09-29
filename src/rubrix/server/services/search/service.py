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

import logging
from typing import Iterable, List, Optional, Type

from fastapi import Depends

from rubrix.server.daos.models.records import DaoRecordsSearch
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.services.datasets import ServiceDataset
from rubrix.server.services.metrics import MetricsService
from rubrix.server.services.metrics.models import ServiceMetric
from rubrix.server.services.search.model import (
    ServiceRecord,
    ServiceRecordsQuery,
    ServiceSearchResults,
    ServiceSortConfig,
)


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
        record_type: Type[ServiceRecord],
        query: Optional[ServiceRecordsQuery] = None,
        sort_config: Optional[ServiceSortConfig] = None,
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
        metrics: Optional[List[ServiceMetric]] = None,
    ) -> ServiceSearchResults:

        if record_from > 0:
            metrics = None

        sort_config = sort_config or ServiceSortConfig()
        exclude_fields = ["metrics.*"] if exclude_metrics else None
        results = self.__dao__.search_records(
            dataset,
            search=DaoRecordsSearch(query=query, sort=sort_config),
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

        return ServiceSearchResults(
            total=results.total,
            records=[record_type.parse_obj(r) for r in results.records],
            metrics=metrics_results if metrics_results else {},
        )

    def scan_records(
        self,
        dataset: ServiceDataset,
        record_type: Type[ServiceRecord],
        query: Optional[ServiceRecordsQuery] = None,
        id_from: Optional[str] = None,
        limit: int = 1000,
    ) -> Iterable[ServiceRecord]:
        """Scan records for a queried"""
        search = DaoRecordsSearch(query=query)
        for doc in self.__dao__.scan_dataset(
            dataset, id_from=id_from, limit=limit, search=search
        ):
            yield record_type.parse_obj(doc)
