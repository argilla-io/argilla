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

from rubrix import MAX_KEYWORD_LENGTH
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
from rubrix.server.tasks.commons.dao import (
    extends_index_properties,
)
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.token_classification.api.model import (
    CreationTokenClassificationRecord,
    MENTIONS_ES_FIELD_NAME,
    PREDICTED_MENTIONS_ES_FIELD_NAME,
    TokenClassificationAggregations,
    TokenClassificationQuery,
    TokenClassificationRecord,
    TokenClassificationSearchResults,
)

extends_index_properties(
    {
        "tokens": {"type": "text"},
        PREDICTED_MENTIONS_ES_FIELD_NAME: {
            "type": "nested",
            "properties": {
                "score": {"type": "float"},
                "mention": {
                    "type": "keyword",
                    "ignore_above": MAX_KEYWORD_LENGTH,
                },
                "entity": {
                    "type": "keyword",
                    "ignore_above": MAX_KEYWORD_LENGTH,
                },
            },
        },
        MENTIONS_ES_FIELD_NAME: {
            "type": "nested",
            "properties": {
                "score": {"type": "float"},
                "mention": {
                    "type": "keyword",
                    "ignore_above": MAX_KEYWORD_LENGTH,
                },
                "entity": {
                    "type": "keyword",
                    "ignore_above": MAX_KEYWORD_LENGTH,
                },
            },
        },
    }
)


class TokenClassificationService:
    """
    Token classification service

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
        records: List[CreationTokenClassificationRecord],
    ):
        self.__metrics__.build_records_metrics(dataset, records)
        failed = self.__dao__.add_records(
            dataset=dataset, records=records, record_class=TokenClassificationRecord
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
                    PREDICTED_MENTIONS_ES_FIELD_NAME: aggregations.nested_aggregation(
                        nested_path=PREDICTED_MENTIONS_ES_FIELD_NAME,
                        inner_aggregation={
                            PREDICTED_MENTIONS_ES_FIELD_NAME: aggregations.bidimentional_terms_aggregations(
                                field_name_x=PREDICTED_MENTIONS_ES_FIELD_NAME
                                + ".entity",
                                field_name_y=PREDICTED_MENTIONS_ES_FIELD_NAME
                                + ".mention",
                            )
                        },
                    ),
                    MENTIONS_ES_FIELD_NAME: aggregations.nested_aggregation(
                        nested_path=MENTIONS_ES_FIELD_NAME,
                        inner_aggregation={
                            MENTIONS_ES_FIELD_NAME: aggregations.bidimentional_terms_aggregations(
                                field_name_x=MENTIONS_ES_FIELD_NAME + ".entity",
                                field_name_y=MENTIONS_ES_FIELD_NAME + ".mention",
                            )
                        },
                    ),
                },
            ),
            size=size,
            record_from=record_from,
            exclude_fields=["metrics"] if exclude_metrics else None
        )
        return TokenClassificationSearchResults(
            total=results.total,
            records=[TokenClassificationRecord.parse_obj(r) for r in results.records],
            aggregations=TokenClassificationAggregations(
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
        for db_record in self.__dao__.scan_dataset(
            dataset, search=RecordSearch(query=query.as_elasticsearch())
        ):
            yield TokenClassificationRecord.parse_obj(db_record)


_instance = None


def token_classification_service(
    dao: DatasetRecordsDAO = Depends(dataset_records_dao),
    metrics: MetricsService = Depends(MetricsService.get_instance),
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
        _instance = TokenClassificationService(
            dao=dao,
            metrics=metrics
        )
    return _instance
