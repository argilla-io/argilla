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

from rubrix.server.commons.es_helpers import sort_by2elasticsearch
from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons import (
    BulkResponse,
    EsRecordDataFieldNames,
    SortableField,
)
from rubrix.server.tasks.commons.dao import extends_index_dynamic_templates
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.text_classification.api.model import (
    CreationTextClassificationRecord,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchAggregations,
    TextClassificationSearchResults,
)

extends_index_dynamic_templates(
    {"inputs": {"path_match": "inputs.*", "mapping": {"type": "text"}}}
)


class TextClassificationService:
    """
    Text classification service

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
        records: List[CreationTextClassificationRecord],
    ):
        self._check_multi_label_integrity(dataset, records)
        self.__metrics__.build_records_metrics(dataset, records)
        failed = self.__dao__.add_records(
            dataset=dataset, records=records, record_class=TextClassificationRecord
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: Dataset,
        query: TextClassificationQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
    ) -> TextClassificationSearchResults:
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
            ),
            size=size,
            record_from=record_from,
        )
        return TextClassificationSearchResults(
            total=results.total,
            records=[TextClassificationRecord.parse_obj(r) for r in results.records],
            aggregations=TextClassificationSearchAggregations(
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
        query: Optional[TextClassificationQuery] = None,
    ) -> Iterable[TextClassificationRecord]:
        """
        Scan a dataset records

        Parameters
        ----------
        dataset:
            The dataset name
        query:
            If provided, scan will retrieve only records matching
            the provided query filters. Optional

        """
        for db_record in self.__dao__.scan_dataset(
            dataset, search=RecordSearch(query=query.as_elasticsearch())
        ):
            yield TextClassificationRecord.parse_obj(db_record)

    def _check_multi_label_integrity(
        self, dataset: Dataset, records: List[TextClassificationRecord]
    ):
        # Fetch a single record
        results = self.search(
            dataset, query=TextClassificationQuery(), size=1, sort_by=[]
        )
        if results.records:
            is_multi_label = records[0].multi_label
            assert is_multi_label == results.records[0].multi_label, (
                "You cannot pass {labels_type} records for this dataset. "
                "Stored records are {labels_type}".format(
                    labels_type="multi-label" if is_multi_label else "single-label"
                )
            )


_instance = None


def text_classification_service(
    dao: DatasetRecordsDAO = Depends(dataset_records_dao),
    metrics: MetricsService = Depends(MetricsService.get_instance),
) -> TextClassificationService:
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
        _instance = TextClassificationService(dao=dao, metrics=metrics)
    return _instance
