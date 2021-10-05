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

import datetime
from typing import Any, Dict, Iterable, List, Optional

from fastapi import Depends
from rubrix.server.datasets.service import DatasetsService, create_dataset_service
from rubrix.server.tasks.commons import (
    BulkResponse,
    EsRecordDataFieldNames,
    SortableField,
)
from rubrix.server.tasks.commons.dao import extends_index_properties
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.commons.es_helpers import (
    aggregations,
    filters,
    sort_by2elasticsearch,
)
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


def as_elasticsearch(search: Text2TextQuery) -> Dict[str, Any]:
    """Build an elasticsearch query part from search query"""

    if search.ids:
        return {"ids": {"values": search.ids}}

    all_filters = filters.metadata(search.metadata)
    query_filters = [
        query_filter
        for query_filter in [
            filters.predicted_by(search.predicted_by),
            filters.annotated_by(search.annotated_by),
            filters.status(search.status),
            filters.predicted(search.predicted),
            filters.score(search.score),
        ]
        if query_filter
    ]
    query_text = filters.text_query(search.query_text)
    all_filters.extend(query_filters)

    return {
        "bool": {
            "must": query_text or {"match_all": {}},
            "filter": {
                "bool": {
                    "should": all_filters,
                    "minimum_should_match": len(all_filters),
                }
            },
        }
    }


class Text2TextService:
    """
    Text2text service

    """

    def __init__(
        self,
        datasets: DatasetsService,
        dao: DatasetRecordsDAO,
    ):
        self.__datasets__ = datasets
        self.__dao__ = dao

    def add_records(
        self,
        dataset: str,
        owner: Optional[str],
        records: List[CreationText2TextRecord],
    ):
        dataset = self.__datasets__.find_by_name(dataset, owner=owner)
        failed = self.__dao__.add_records(
            dataset=dataset,
            records=records,
            record_class=Text2TextRecordDB,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: str,
        owner: Optional[str],
        query: Text2TextQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
    ) -> Text2TextSearchResults:
        """
        Run a search in a dataset

        Parameters
        ----------
        dataset:
            The dataset name
        owner:
            The dataset owner
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
        dataset = self.__datasets__.find_by_name(dataset, owner=owner)

        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(
                query=as_elasticsearch(query),
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
        )
        return Text2TextSearchResults(
            total=results.total,
            records=[Text2TextRecord.parse_obj(r) for r in results.records],
            metrics=results.metrics,
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
        dataset: str,
        owner: Optional[str],
        query: Optional[Text2TextQuery] = None,
    ) -> Iterable[Text2TextRecord]:
        """
        Scan a dataset records

        Parameters
        ----------
        dataset:
            The dataset name
        owner:
            The dataset owner. Optional
        query:
            If provided, scan will retrieve only records matching
            the provided query filters. Optional

        """
        dataset = self.__datasets__.find_by_name(dataset, owner=owner)
        for db_record in self.__dao__.scan_dataset(
            dataset, search=RecordSearch(query=as_elasticsearch(query))
        ):
            yield Text2TextRecord.parse_obj(db_record)


_instance = None


def text2text_service(
    datasets: DatasetsService = Depends(create_dataset_service),
    dao: DatasetRecordsDAO = Depends(dataset_records_dao),
) -> Text2TextService:
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
        _instance = Text2TextService(datasets=datasets, dao=dao)
    return _instance
