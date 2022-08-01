#  coding=utf-8
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

from typing import Iterable, List, Optional, Type

from fastapi import Depends

from rubrix.server.apis.v0.models.metrics.base import BaseTaskMetrics
from rubrix.server.backend.search.model import SortableField
from rubrix.server.services.metrics import BaseMetric
from rubrix.server.services.search.model import SortConfig
from rubrix.server.services.search.service import SearchRecordsService
from rubrix.server.services.storage.service import RecordsStorageService
from rubrix.server.services.tasks.commons import BulkResponse
from rubrix.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord,
    TokenClassificationAggregations,
    TokenClassificationDatasetDB,
    TokenClassificationQuery,
    TokenClassificationSearchResults,
)


class TokenClassificationService:
    """
    Token classification service

    """

    _INSTANCE: "TokenClassificationService" = None

    @classmethod
    def get_instance(
        cls,
        storage: RecordsStorageService = Depends(RecordsStorageService.get_instance),
        search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
    ):
        if not cls._INSTANCE:
            cls._INSTANCE = cls(storage, search)
        return cls._INSTANCE

    def __init__(
        self,
        storage: RecordsStorageService,
        search: SearchRecordsService,
    ):
        self.__storage__ = storage
        self.__search__ = search

    def add_records(
        self,
        dataset: TokenClassificationDatasetDB,
        records: List[ServiceTokenClassificationRecord],
        metrics: Type[BaseTaskMetrics],
    ):
        failed = self.__storage__.store_records(
            dataset=dataset,
            records=records,
            record_type=ServiceTokenClassificationRecord,
            metrics=metrics,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: TokenClassificationDatasetDB,
        query: TokenClassificationQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
        metrics: Optional[List[BaseMetric]] = None,
    ) -> TokenClassificationSearchResults:

        results = self.__search__.search(
            dataset,
            query=query,
            record_type=ServiceTokenClassificationRecord,
            size=size,
            record_from=record_from,
            exclude_metrics=exclude_metrics,
            metrics=metrics,
            sort_config=SortConfig(sort_by=sort_by),
        )

        if results.metrics:
            results.metrics["words"] = results.metrics["words_cloud"]
            results.metrics["status"] = results.metrics["status_distribution"]
            results.metrics["predicted"] = results.metrics["error_distribution"]
            results.metrics["predicted"].pop("unknown", None)
            results.metrics["mentions"] = results.metrics[
                "annotated_mentions_distribution"
            ]
            results.metrics["predicted_mentions"] = results.metrics[
                "predicted_mentions_distribution"
            ]

        return TokenClassificationSearchResults(
            total=results.total,
            records=results.records,
            aggregations=TokenClassificationAggregations.parse_obj(results.metrics)
            if results.metrics
            else None,
        )

    def read_dataset(
        self,
        dataset: TokenClassificationDatasetDB,
        query: TokenClassificationQuery,
    ) -> Iterable[ServiceTokenClassificationRecord]:
        """
        Scan a dataset records

        Parameters
        ----------
        dataset:
            The dataset name
        owner:
            The dataset owner
        query:
            If provided, scan will retrieve only records matching
            the provided query filters. Optional

        """
        yield from self.__search__.scan_records(
            dataset, query=query, record_type=ServiceTokenClassificationRecord
        )
