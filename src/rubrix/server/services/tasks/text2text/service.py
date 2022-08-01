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

# TODO(@frascuchon): ESTO NO!!!
from rubrix.server.apis.v0.models.metrics.base import BaseTaskMetrics
from rubrix.server.services.metrics import BaseMetric
from rubrix.server.services.search.model import SortableField, SortConfig
from rubrix.server.services.search.service import SearchRecordsService
from rubrix.server.services.storage.service import RecordsStorageService
from rubrix.server.services.tasks.commons import BulkResponse
from rubrix.server.services.tasks.text2text.models import (
    ServiceText2TextRecord,
    Text2TextDatasetDB,
    Text2TextQuery,
    Text2TextSearchAggregations,
    Text2TextSearchResults,
)


class Text2TextService:
    """
    Text2text service

    """

    _INSTANCE: "Text2TextService" = None

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
        dataset: Text2TextDatasetDB,
        records: List[ServiceText2TextRecord],
        metrics: Type[
            BaseTaskMetrics
        ],  # TODO(@frascuchon): Remove this method and resolve in backend
    ):
        failed = self.__storage__.store_records(
            dataset=dataset,
            records=records,
            record_type=ServiceText2TextRecord,
            metrics=metrics,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: Text2TextDatasetDB,
        query: Text2TextQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
        metrics: Optional[List[BaseMetric]] = None,
    ) -> Text2TextSearchResults:
        """
        Run a search in a dataset

        Parameters
        ----------
        dataset:
            The records dataset
        query:
            The search parameters
        sort_by:
            The sort by list
        record_from:
            The record from return results
        size:
            The max number of records to return

        Returns
        -------
            The matched records with aggregation info for specified task_meta.py

        """

        results = self.__search__.search(
            dataset,
            query=query,
            size=size,
            record_from=record_from,
            record_type=ServiceText2TextRecord,
            sort_config=SortConfig(
                sort_by=sort_by,
            ),
            exclude_metrics=exclude_metrics,
            metrics=metrics,
        )

        if results.metrics:
            results.metrics["words"] = results.metrics["words_cloud"]
            results.metrics["status"] = results.metrics["status_distribution"]

        return Text2TextSearchResults(
            total=results.total,
            records=results.records,
            aggregations=Text2TextSearchAggregations.parse_obj(results.metrics)
            if results.metrics
            else None,
        )

    def read_dataset(
        self,
        dataset: Text2TextDatasetDB,
        query: Optional[Text2TextQuery] = None,
    ) -> Iterable[ServiceText2TextRecord]:
        """
        Scan a dataset records

        Parameters
        ----------
        dataset:
            The records dataset
        query:
            If provided, scan will retrieve only records matching
            the provided query filters. Optional

        """
        yield from self.__search__.scan_records(
            dataset, query=query, record_type=ServiceText2TextRecord
        )
