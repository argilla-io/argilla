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
from argilla.server.services.datasets import ServiceDataset
from argilla.server.services.search.model import (
    ServiceSearchResults,
    ServiceSortableField,
    ServiceSortConfig,
)
from argilla.server.services.search.service import SearchRecordsService
from argilla.server.services.storage.service import RecordsStorageService
from argilla.server.services.tasks.commons import BulkResponse
from argilla.server.services.tasks.text2text.models import (
    ServiceText2TextQuery,
    ServiceText2TextRecord,
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

    async def add_records(
        self,
        dataset: ServiceDataset,
        records: List[ServiceText2TextRecord],
    ):
        failed = await self.__storage__.store_records(
            dataset=dataset,
            records=records,
            record_type=ServiceText2TextRecord,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: ServiceDataset,
        query: ServiceText2TextQuery,
        sort_by: List[ServiceSortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
    ) -> ServiceSearchResults:
        metrics = TasksFactory.find_task_metrics(
            dataset.task,
            metric_ids={
                "words_cloud",
                "predicted_by",
                "annotated_by",
                "status_distribution",
                "metadata",
                "score",
            },
        )

        results = self.__search__.search(
            dataset,
            query=query,
            size=size,
            record_from=record_from,
            record_type=ServiceText2TextRecord,
            sort_config=ServiceSortConfig(
                sort_by=sort_by,
            ),
            exclude_metrics=exclude_metrics,
            metrics=metrics,
        )

        if results.metrics:
            results.metrics["words"] = results.metrics.get("words_cloud", {})
            results.metrics["status"] = results.metrics["status_distribution"]

        return results

    def read_dataset(
        self,
        dataset: ServiceDataset,
        query: Optional[ServiceText2TextQuery] = None,
        id_from: Optional[str] = None,
        limit: int = 1000,
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
        id_from:
            If provided, read the samples after this record ID
        limit:
            Batch size to scan, only used if `id_from` is specified

        """
        yield from self.__search__.scan_records(
            dataset,
            query=query,
            record_type=ServiceText2TextRecord,
            id_from=id_from,
            limit=limit,
        )
