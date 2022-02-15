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

from typing import Iterable, List

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
from rubrix.server.tasks.token_classification.api.model import (
    CreationTokenClassificationRecord,
    TokenClassificationAggregations,
    TokenClassificationQuery,
    TokenClassificationRecord,
    TokenClassificationRecordDB,
    TokenClassificationSearchResults,
)
from rubrix.server.tasks.token_classification.dao.es_config import (
    token_classification_mappings,
)


class TokenClassificationService:
    """
    Token classification service

    """

    def __init__(
        self,
        dao: DatasetRecordsDAO,
        metrics: MetricsService,
        search: SearchRecordsService,
    ):
        self.__dao__ = dao
        self.__metrics__ = metrics
        self.__search__ = search

        self.__dao__.register_task_mappings(
            TaskType.token_classification, token_classification_mappings()
        )

    def add_records(
        self,
        dataset: Dataset,
        records: List[CreationTokenClassificationRecord],
    ):
        self.__metrics__.build_records_metrics(dataset, records)
        failed = self.__dao__.add_records(
            dataset=dataset,
            records=records,
            record_class=TokenClassificationRecordDB,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: Dataset,
        query: TokenClassificationQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
    ) -> TokenClassificationSearchResults:
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

        results = self.__search__.search(
            dataset,
            query=query,
            record_type=TokenClassificationRecord,
            size=size,
            record_from=record_from,
            exclude_metrics=exclude_metrics,
            metrics={
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
            sort_config=SortConfig(
                sort_by=sort_by,
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
        dataset: Dataset,
        query: TokenClassificationQuery,
    ) -> Iterable[TokenClassificationRecord]:
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
            dataset, query=query, record_type=TokenClassificationRecord
        )


_instance = None


def token_classification_service(
    dao: DatasetRecordsDAO = Depends(dataset_records_dao),
    metrics: MetricsService = Depends(MetricsService.get_instance),
    search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
) -> TokenClassificationService:
    """
    Creates a dataset record service instance

    Parameters
    ----------
    datasets:
        The datasets service dependency
    dao:
        The dataset records dao dependency

    Returns
    -------
        A dataset records service instance
    """
    global _instance
    if not _instance:
        _instance = TokenClassificationService(dao=dao, metrics=metrics, search=search)
    return _instance
