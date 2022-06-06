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

from typing import Any, Dict, Iterable, List, Optional, Type

from fastapi import Depends

from rubrix.server.apis.v0.models.commons.model import (
    BulkResponse,
    EsRecordDataFieldNames,
    SortableField,
)
from rubrix.server.apis.v0.models.metrics.base import BaseMetric, BaseTaskMetrics
from rubrix.server.apis.v0.models.text2text import (
    CreationText2TextRecord,
    Text2TextDatasetDB,
    Text2TextQuery,
    Text2TextRecord,
    Text2TextRecordDB,
    Text2TextSearchAggregations,
    Text2TextSearchResults,
)
from rubrix.server.services.search.model import SortConfig
from rubrix.server.services.search.service import SearchRecordsService
from rubrix.server.services.storage.service import RecordsStorageService


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
        mappings: Dict[str, Any],
        records: List[CreationText2TextRecord],
        metrics: Type[BaseTaskMetrics],
    ):
        failed = self.__storage__.store_records(
            dataset=dataset,
            mappings=mappings,
            records=records,
            record_type=Text2TextRecordDB,
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
            record_type=Text2TextRecord,
            sort_config=SortConfig(
                sort_by=sort_by,
                valid_fields=[
                    "metadata",
                    EsRecordDataFieldNames.predicted_as,
                    EsRecordDataFieldNames.annotated_as,
                    EsRecordDataFieldNames.predicted_by,
                    EsRecordDataFieldNames.annotated_by,
                    EsRecordDataFieldNames.status,
                    EsRecordDataFieldNames.last_updated,
                    EsRecordDataFieldNames.event_timestamp,
                ],
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
    ) -> Iterable[Text2TextRecord]:
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
            dataset, query=query, record_type=Text2TextRecord
        )


text2text_service = Text2TextService.get_instance
