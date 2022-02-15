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

from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons import (
    BulkResponse,
    EsRecordDataFieldNames,
    SortableField,
    TaskType,
)
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.search.model import SortConfig
from rubrix.server.tasks.search.service import SearchRecordsService
from rubrix.server.tasks.text2text.api.model import (
    CreationText2TextRecord,
    Text2TextQuery,
    Text2TextRecord,
    Text2TextRecordDB,
    Text2TextSearchAggregations,
    Text2TextSearchResults,
)
from rubrix.server.tasks.text2text.dao.es_config import text2text_mappings


class Text2TextService:
    """
    Text2text service

    """

    def __init__(
        self,
        dao: DatasetRecordsDAO,
        search: SearchRecordsService,
        metrics: MetricsService,
    ):
        self.__dao__ = dao
        self.__metrics__ = metrics
        self.__search__ = search

        self.__dao__.register_task_mappings(TaskType.text2text, text2text_mappings())

    def add_records(
        self,
        dataset: Dataset,
        records: List[CreationText2TextRecord],
    ):
        self.__metrics__.build_records_metrics(dataset, records)
        failed = self.__dao__.add_records(
            dataset=dataset,
            records=records,
            record_class=Text2TextRecordDB,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: Dataset,
        query: Text2TextQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
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
            metrics={
                "words_cloud",
                "predicted_by",
                "annotated_by",
                "status_distribution",
                "metadata",
                "score",
            },
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
        dataset: Dataset,
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


_instance = None


def text2text_service(
    dao: DatasetRecordsDAO = Depends(dataset_records_dao),
    metrics: MetricsService = Depends(MetricsService.get_instance),
    search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
) -> Text2TextService:
    """
    Creates a dataset record service instance

    Parameters
    ----------
    dao:
        The dataset records dao dependency
    metrics:
        The metrics service

    Returns
    -------
        A dataset records service instance
    """
    global _instance
    if not _instance:
        _instance = Text2TextService(dao=dao, metrics=metrics, search=search)
    return _instance
