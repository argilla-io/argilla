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
from typing import Any, Dict, Iterable, List, Optional, Type

import deprecated
from fastapi import Depends

from rubrix.server.backend.elasticsearch import (
    ClosedIndexError,
    ElasticsearchBackend,
    IndexNotFoundError,
    create_es_wrapper,
)

# TODO(@frascuchon): Move this to the backend
from rubrix.server.backend.mappings.datasets import DATASETS_RECORDS_INDEX_NAME
from rubrix.server.backend.mappings.helpers import (
    mappings,
    tasks_common_mappings,
    tasks_common_settings,
)
from rubrix.server.backend.search.model import BackendRecordsQuery
from rubrix.server.daos.models.datasets import DAODatasetDB
from rubrix.server.daos.models.records import (
    DAORecordDB,
    RecordSearch,
    RecordSearchResults,
)
from rubrix.server.errors import ClosedDatasetError, MissingDatasetRecordsError
from rubrix.server.errors.task_errors import MetadataLimitExceededError
from rubrix.server.settings import settings


# TODO(@frascuchon): Move to the backend and accept the dataset id as parameter
def dataset_records_index(dataset_id: str) -> str:
    """
    Returns dataset records index for a given dataset id

    The dataset info is stored in two elasticsearch indices. The main
    index where all datasets definition are stored and
    an specific dataset index for data records.

    This function calculates the corresponding dataset records index
    for a given dataset id.

    Parameters
    ----------
    dataset_id

    Returns
    -------
        The dataset records index name

    """
    return DATASETS_RECORDS_INDEX_NAME.format(dataset_id)


class DatasetRecordsDAO:
    """Datasets records DAO"""

    _INSTANCE = None

    # Keep info about elasticsearch mappings per task
    # This info must be provided by each task using dao.register_task_mappings method
    _MAPPINGS_BY_TASKS = {}

    @classmethod
    def get_instance(
        cls,
        es: ElasticsearchBackend = Depends(ElasticsearchBackend.get_instance),
    ) -> "DatasetRecordsDAO":
        """
        Creates a dataset records dao instance

        Parameters
        ----------
        es:
            The elasticserach wrapper dependency

        """
        if not cls._INSTANCE:
            cls._INSTANCE = cls(es)
        return cls._INSTANCE

    def __init__(self, es: ElasticsearchBackend):
        self._es = es

    def init(self):
        """Initializes dataset records dao. Used on app startup"""
        pass

    def add_records(
        self,
        dataset: DAODatasetDB,
        records: List[DAORecordDB],
        record_class: Type[DAORecordDB],
    ) -> int:
        """
        Add records to dataset

        Parameters
        ----------
        dataset:
            The dataset
        records:
            The list of records
        record_class:
            ServiceRecord class used to convert records to
        Returns
        -------
            The number of failed records

        """

        now = None
        documents = []
        metadata_values = {}

        if "last_updated" in record_class.schema()["properties"]:
            now = datetime.datetime.utcnow()

        for r in records:
            metadata_values.update(r.metadata or {})
            db_record = record_class.parse_obj(r)
            if now:
                db_record.last_updated = now
            documents.append(
                db_record.dict(exclude_none=False, exclude={"search_keywords"})
            )

        index_name = self.create_dataset_index(dataset)
        self._configure_metadata_fields(index_name, metadata_values)
        return self._es.add_documents(
            index=index_name,
            documents=documents,
            doc_id=lambda _record: _record.get("id"),
        )

    def get_metadata_schema(self, dataset: DAODatasetDB) -> Dict[str, str]:
        """Get metadata fields schema for provided dataset"""
        records_index = dataset_records_index(dataset.id)
        return self._es.get_field_mapping(index=records_index, field_name="metadata.*")

    def compute_metric(
        self,
        dataset: DAODatasetDB,
        metric_id: str,
        metric_params: Dict[str, Any] = None,
        query: Optional[BackendRecordsQuery] = None,
    ):
        """
        Parameters
        ----------
        metric_id:
            The backend metric id
        metric_params:
            The summary params
        dataset:
            The records dataset
        query:
            The filter to apply to dataset

        Returns
        -------
            The metric summary result

        """
        return self._es.compute_metric(
            index=dataset_records_index(dataset.id),
            metric_id=metric_id,
            query=query,
            params=metric_params,
        )

    def search_records(
        self,
        dataset: DAODatasetDB,
        search: Optional[RecordSearch] = None,
        size: int = 100,
        record_from: int = 0,
        exclude_fields: List[str] = None,
        highligth_results: bool = True,
    ) -> RecordSearchResults:
        """
        SearchRequest records under a dataset given a search parameters.

        Parameters
        ----------
        dataset:
            The dataset
        search:
            The search params
        size:
            Number of records to retrieve (for pagination)
        record_from:
            ServiceRecord from which to retrieve the records (for pagination)
        exclude_fields:
            a list of fields to exclude from the result source. Wildcards are accepted
        Returns
        -------
            The search result

        """
        # TODO(@frascuchon): Move this logic to the backend class
        try:
            search = search or RecordSearch()
            records_index = dataset_records_index(dataset.id)

            total, records = self._es.search_records(
                index=records_index,
                query=search.query,
                sort=search.sort,
                record_from=record_from,
                size=size,
                exclude_fields=exclude_fields,
                enable_highlight=highligth_results,
            )
            return RecordSearchResults(total=total, records=records)
        except ClosedIndexError:
            raise ClosedDatasetError(dataset.name)
        except IndexNotFoundError:
            raise MissingDatasetRecordsError(
                f"No records index found for dataset {dataset.name}"
            )

    def scan_dataset(
        self,
        dataset: DAODatasetDB,
        search: Optional[RecordSearch] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Iterates over a dataset records

        Parameters
        ----------
        dataset:
            The dataset
        search:
            The search parameters. Optional

        Returns
        -------
            An iterable over found dataset records
        """
        search = search or RecordSearch()
        return self._es.scan_records(
            index=dataset_records_index(dataset.id), query=search.query
        )

    def _configure_metadata_fields(self, index: str, metadata_values: Dict[str, Any]):
        def check_metadata_length(metadata_length: int = 0):
            if metadata_length > settings.metadata_fields_limit:
                raise MetadataLimitExceededError(
                    length=metadata_length, limit=settings.metadata_fields_limit
                )

        def detect_nested_type(v: Any) -> bool:
            """Returns True if value match as nested value"""
            return isinstance(v, list) and isinstance(v[0], dict)

        check_metadata_length(len(metadata_values))
        check_metadata_length(
            len(
                {
                    *self._es.get_field_mapping(index, "metadata.*"),
                    *[k for k in metadata_values.keys()],
                }
            )
        )
        for field, value in metadata_values.items():
            if detect_nested_type(value):
                self._es.create_field_mapping(
                    index,
                    field_name=f"metadata.{field}",
                    mapping=mappings.nested_field(),
                )

    def create_dataset_index(
        self,
        dataset: DAODatasetDB,
        force_recreate: bool = False,
    ) -> str:
        """
        Creates a dataset records elasticsearch index based on dataset task type

        Args:
            dataset:
                The dataset
            force_recreate:
                If True, the index will be deleted and recreated

        Returns:
            The generated index name.
        """
        _mappings = tasks_common_mappings()
        task_mappings = self._es.get_task_mapping(dataset.task).copy()
        for k in task_mappings:
            if isinstance(task_mappings[k], list):
                _mappings[k] = [*_mappings.get(k, []), *task_mappings[k]]
            else:
                _mappings[k] = {**_mappings.get(k, {}), **task_mappings[k]}

        index_name = dataset_records_index(dataset.id)
        self._es.create_index(
            index=index_name,
            settings=tasks_common_settings(),
            mappings={**tasks_common_mappings(), **_mappings},
            force_recreate=force_recreate,
        )
        return index_name

    def get_dataset_schema(self, dataset: DAODatasetDB) -> Dict[str, Any]:
        """Return inner elasticsearch index configuration"""
        schema = self._es.get_index_mapping(dataset_records_index(dataset.id))
        return schema
