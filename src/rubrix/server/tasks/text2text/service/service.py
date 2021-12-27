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

from rubrix.server.commons.es_helpers import (
    aggregations,
    sort_by2elasticsearch,
)
from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons import (
    BulkResponse,
    EsRecordDataFieldNames,
    SortableField,
)
from rubrix.server.tasks.commons.dao import extends_index_properties
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.text2text.api.model import (
    CreationText2TextRecord,
    ExtendedEsRecordDataFieldNames,
    Text2TextQuery,
    Text2TextRecord,
    Text2TextRecordDB,
    Text2TextSearchAggregations,
    Text2TextSearchResults,
)

extends_index_properties(
    {
        ExtendedEsRecordDataFieldNames.text_predicted: {
            "type": "text",
            "fielddata": True,
            "analyzer": "multilingual_stop_analyzer",
            "fields": {"extended": {"type": "text", "analyzer": "extended_analyzer"}},
        },
        ExtendedEsRecordDataFieldNames.text_annotated: {
            "type": "text",
            "fielddata": True,
            "analyzer": "multilingual_stop_analyzer",
            "fields": {"extended": {"type": "text", "analyzer": "extended_analyzer"}},
        },
    }
)


class Text2TextService:
    """
    Text2text service

    """

    def __init__(
        self,
        dao: DatasetRecordsDAO,
        metrics: MetricsService,
    ):
        self.__dao__ = dao
        self.__metrics__ = metrics

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
        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(
                query=query.as_elasticsearch(),
                sort=sort_by2elasticsearch(
                    sort_by,
                    valid_fields=[
                        "metadata",
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
                aggregations={
                    ExtendedEsRecordDataFieldNames.text_predicted: aggregations.terms_aggregation(
                        ExtendedEsRecordDataFieldNames.text_predicted
                    )
                },
            ),
            size=size,
            record_from=record_from,
            exclude_fields=["metrics"] if exclude_metrics else None,
        )
        return Text2TextSearchResults(
            total=results.total,
            records=[Text2TextRecord.parse_obj(r) for r in results.records],
            aggregations=Text2TextSearchAggregations(
                **results.aggregations,
                words=results.words,
                metadata=results.metadata or {},
            )
            if results.aggregations
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
        for db_record in self.__dao__.scan_dataset(
            dataset, search=RecordSearch(query=query.as_elasticsearch())
        ):
            yield Text2TextRecord.parse_obj(db_record)


_instance = None


def text2text_service(
    dao: DatasetRecordsDAO = Depends(dataset_records_dao),
    metrics: MetricsService = Depends(MetricsService.get_instance),
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
        _instance = Text2TextService(dao=dao, metrics=metrics)
    return _instance
