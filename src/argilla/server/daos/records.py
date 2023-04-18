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
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type

from fastapi import Depends

from argilla.server.daos.backend import GenericElasticEngineBackend
from argilla.server.daos.backend.base import ClosedIndexError, IndexNotFoundError
from argilla.server.daos.backend.generic_elastic import PaginatedSortInfo
from argilla.server.daos.backend.search.model import BaseRecordsQuery, SortableField
from argilla.server.daos.models.datasets import DatasetDB
from argilla.server.daos.models.records import (
    DaoRecordsSearch,
    DaoRecordsSearchResults,
    RecordDB,
)
from argilla.server.errors import ClosedDatasetError, MissingDatasetRecordsError


class DatasetRecordsDAO:
    """Datasets records DAO"""

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        es: GenericElasticEngineBackend = Depends(GenericElasticEngineBackend.get_instance),
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

    def __init__(self, es: GenericElasticEngineBackend):
        self._es = es

    def init(self):
        """Initializes dataset records dao. Used on app startup"""
        pass

    def add_records(
        self,
        dataset: DatasetDB,
        records: List[RecordDB],
        record_class: Type[RecordDB],
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
            Record class used to convert records to
        Returns
        -------
            The number of failed records

        """

        now = datetime.datetime.utcnow()
        documents = []
        metadata_values = {}

        mapping = self._es.get_schema(id=dataset.id)
        exclude_fields = [
            name for name in record_class.schema()["properties"] if name not in mapping["mappings"]["properties"]
        ]

        vectors_configuration = {}
        for record in records:
            metadata_values.update(record.metadata or {})

            db_record = record_class.parse_obj(record)
            db_record.last_updated = now

            record_dict = db_record.dict(exclude_none=True, exclude=set(exclude_fields))

            if record.vectors is not None:
                # TODO: Create embeddings config by settings
                for (
                    vector_name,
                    vector_data_mapping,
                ) in record.vectors.items():
                    vector_dimension = vectors_configuration.get(vector_name, None)

                    if vector_dimension is None:
                        dimension = len(vector_data_mapping.value)
                        vectors_configuration[vector_name] = dimension

            documents.append(record_dict)

        self._es.create_dataset(
            id=dataset.id,
            task=dataset.task,
            metadata_values=metadata_values,
            vectors_cfg=vectors_configuration,
        )

        return self._es.add_dataset_records(
            id=dataset.id,
            documents=documents,
        )

    def compute_metric(
        self,
        dataset: DatasetDB,
        metric_id: str,
        metric_params: Dict[str, Any] = None,
        query: Optional[BaseRecordsQuery] = None,
    ):
        return self._es.compute_metric(
            id=dataset.id,
            metric_id=metric_id,
            query=query,
            params=metric_params,
        )

    def search_records(
        self,
        dataset: DatasetDB,
        search: Optional[DaoRecordsSearch] = None,
        size: int = 100,
        record_from: int = 0,
        exclude_fields: List[str] = None,
        highligth_results: bool = True,
    ) -> DaoRecordsSearchResults:
        try:
            search = search or DaoRecordsSearch()

            total, records = self._es.search_records(
                id=dataset.id,
                query=search.query,
                sort=search.sort,
                record_from=record_from,
                size=size,
                exclude_fields=exclude_fields,
                enable_highlight=highligth_results,
            )
            if isinstance(total, dict):
                total = total["value"]
            return DaoRecordsSearchResults(
                total=total,
                records=records,
            )
        except ClosedIndexError:
            raise ClosedDatasetError(dataset.name)
        except IndexNotFoundError:
            raise MissingDatasetRecordsError(f"No records index found for dataset {dataset.name}")

    def scan_dataset(
        self,
        dataset: DatasetDB,
        search: Optional[DaoRecordsSearch] = None,
        limit: Optional[int] = 1000,
        id_from: Optional[str] = None,
        include_fields: Optional[Set[str]] = None,
        exclude_fields: Optional[Set[str]] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Iterates over a dataset records

        Parameters
        ----------
        dataset:
            The dataset
        search:
            The search parameters. Optional
        limit:
            Batch size to extract, only works if an `id_from` is provided
        id_from:
            From which ID should we start iterating
        include_fields:
            A set of record fields to retrieve. Wildcard are allowed
        exclude_fields:
            A set of record fields to exclude. Wildcard are allowed

        Returns
        -------
            An iterable over found dataset records
        """

        search = search or DaoRecordsSearch()
        next_search_params = [id_from] if id_from else None
        paginated_sort = PaginatedSortInfo(
            sort_by=[SortableField(id="id")], shuffle=search.sort.shuffle, next_search_params=next_search_params
        )

        return self._es.scan_records(
            id=dataset.id,
            query=search.query,
            sort=paginated_sort,
            limit=limit,
            include_fields=list(include_fields) if include_fields else None,
            exclude_fields=list(exclude_fields) if exclude_fields else None,
        )

    async def delete_records_by_query(
        self,
        dataset: DatasetDB,
        query: Optional[BaseRecordsQuery] = None,
    ) -> Tuple[int, int]:
        total, deleted = await self._es.delete_records_by_query(
            id=dataset.id,
            query=query,
        )
        return total, deleted

    async def update_records_by_query(
        self,
        dataset: DatasetDB,
        query: Optional[BaseRecordsQuery] = None,
        **content,
    ) -> Tuple[int, int]:
        total, updated = await self._es.update_records_content(
            id=dataset.id,
            content=content,
            query=query,
        )
        return total, updated

    async def update_record(
        self,
        dataset: DatasetDB,
        record: RecordDB,
    ):
        self._es.update_record(
            dataset_id=dataset.id,
            record_id=record.id,
            content=record.dict(exclude_none=True),
        )

    async def get_record_by_id(
        self,
        dataset: DatasetDB,
        id: str,
    ) -> Optional[Dict[str, Any]]:
        return self._es.find_record_by_id(
            dataset_id=dataset.id,
            record_id=id,
        )
