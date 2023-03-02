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

from typing import Iterable, List, Optional

from fastapi import Depends

from argilla.server.commons.config import TasksFactory
from argilla.server.daos.backend.search.model import SortableField
from argilla.server.services.datasets import ServiceBaseDataset
from argilla.server.services.search.model import ServiceSearchResults, ServiceSortConfig
from argilla.server.services.search.service import SearchRecordsService
from argilla.server.services.storage.service import RecordsStorageService
from argilla.server.services.tasks.commons import BulkResponse
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationQuery,
    ServiceTokenClassificationRecord,
)


class TokenClassificationService:
    """
    Token classification service

    """

    _INSTANCE: Optional["TokenClassificationService"] = None

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

    async def add_records(
        self,
        dataset: ServiceBaseDataset,
        records: List[ServiceTokenClassificationRecord],
    ):
        failed = await self.__storage__.store_records(
            dataset=dataset,
            records=records,
            record_type=ServiceTokenClassificationRecord,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: ServiceBaseDataset,
        query: ServiceTokenClassificationQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
    ) -> ServiceSearchResults:
        """
        Run a search in a dataset

        Parameters
        ----------
        dataset:
            The records dataset
        query:
            The search parameters
        sort_by:
            The sort by order list
        record_from:
            The record from return results
        size:
            The max number of records to return

        Returns
        -------
            The matched records with aggregation info for specified task_meta.py

        """
        metrics = TasksFactory.find_task_metrics(
            dataset.task,
            metric_ids={
                "words_cloud",
                "predicted_by",
                "predicted_as",
                "annotated_by",
                "annotated_as",
                "error_distribution",
                "predicted_mentions_distribution",
                "annotated_mentions_distribution",
                "status_distribution",
                "metadata",
                "score",
            },
        )

        results = self.__search__.search(
            dataset,
            query=query,
            record_type=ServiceTokenClassificationRecord,
            size=size,
            metrics=metrics,
            record_from=record_from,
            exclude_metrics=exclude_metrics,
            sort_config=ServiceSortConfig(sort_by=sort_by),
        )

        if results.metrics:
            results.metrics["words"] = results.metrics.get("words_cloud", {})
            results.metrics["status"] = results.metrics["status_distribution"]
            results.metrics["predicted"] = results.metrics["error_distribution"]
            results.metrics["predicted"].pop("unknown", None)
            results.metrics["mentions"] = results.metrics["annotated_mentions_distribution"]
            results.metrics["predicted_mentions"] = results.metrics["predicted_mentions_distribution"]

        return results

    def read_dataset(
        self,
        dataset: ServiceBaseDataset,
        query: ServiceTokenClassificationQuery,
        id_from: Optional[str] = None,
        limit: int = 1000,
    ) -> Iterable[ServiceTokenClassificationRecord]:
        """
        Scan a dataset records

        Parameters
        ----------
        dataset:
            The dataset name
        query:
            If provided, scan will retrieve only records matching
            the provided query filters. Optional
        id_from:
            If provided, read the samples after this record ID
        limit:
            Batch size to scan, only used if `id_from` is specified

        """
        yield from self.__search__.scan_records(
            dataset,
            query=query,
            record_type=ServiceTokenClassificationRecord,
            id_from=id_from,
            limit=limit,
        )
