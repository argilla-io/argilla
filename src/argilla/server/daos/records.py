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
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type

from fastapi import Depends

from argilla.server.daos.backend.elasticsearch import (
    ClosedIndexError,
    ElasticsearchBackend,
    IndexNotFoundError,
)
from argilla.server.daos.backend.search.model import BackendRecordsQuery
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
            name
            for name in record_class.schema()["properties"]
            if name not in mapping["mappings"]["properties"]
        ]
        embedding_index_name_2_dimension = {}
        for r in records:
            metadata_values.update(r.metadata or {})
            db_record = record_class.parse_obj(r)
            db_record.last_updated = now
            if db_record.embeddings is not None:
                for embedding in db_record.embeddings:
                    for embedding_property_name_2_value in embedding.embeddings:
                        if hasattr(embedding_property_name_2_value, "propertyNames"):
                            embedding_property_name = "_".join(
                                embedding_property_name_2_value.propertyNames
                            )
                        elif hasattr(embedding_property_name_2_value, "property_name"):
                            embedding_property_name = (
                                embedding_property_name_2_value.property_name
                            )
                        else:
                            embedding_property_name = "this"
                        embedding_name = ".".join(
                            [embedding.record_property_name, embedding_property_name]
                        )
                        for (
                            embedding_vector
                        ) in embedding_property_name_2_value.embedding_vectors:
                            embedding_index_name = (
                                embedding_name + "_" + embedding_vector.vectorizer_name
                            )
                            embedding_dimension = len(embedding_vector.embedding_vector)
                            expected_dimension = embedding_index_name_2_dimension.get(
                                embedding_index_name, None
                            )
                            if expected_dimension is None:
                                embedding_index_name_2_dimension[
                                    embedding_index_name
                                ] = embedding_dimension
                                continue
                            ## we can drop these two if statements, keeping them for discussion purpose
                            if embedding_dimension != expected_dimension:
                                ## there is inconsistency keep the previous, @frascuchon lets discuss about potential issues
                                continue
                            if embedding_dimension == expected_dimension:
                                continue  ## everything is fine

            documents.append(
                db_record.dict(
                    exclude_none=False,
                    exclude=set(exclude_fields),
                )
            )

        self._es.create_dataset_index(
            id=dataset.id,
            task=dataset.task,
            metadata_values=metadata_values,
            embeddings_cfg=embedding_index_name_2_dimension,  # TODO(@ufuk): this field should be computed from the provided info in records
        )

        return self._es.add_documents(
            id=dataset.id,
            documents=documents,
        )

    def get_metadata_schema(self, dataset: DatasetDB) -> Dict[str, str]:
        """Get metadata fields schema for provided dataset"""

        return self._es.get_metadata_mappings(id=dataset.id)

    def compute_metric(
        self,
        dataset: DatasetDB,
        metric_id: str,
        metric_params: Dict[str, Any] = None,
        query: Optional[BackendRecordsQuery] = None,
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
            return DaoRecordsSearchResults(total=total, records=records)
        except ClosedIndexError:
            raise ClosedDatasetError(dataset.name)
        except IndexNotFoundError:
            raise MissingDatasetRecordsError(
                f"No records index found for dataset {dataset.name}"
            )

    def scan_dataset(
        self,
        dataset: DatasetDB,
        search: Optional[DaoRecordsSearch] = None,
        limit: int = 1000,
        id_from: Optional[str] = None,
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

        Returns
        -------
            An iterable over found dataset records
        """
        search = search or DaoRecordsSearch()
        return self._es.scan_records(
            id=dataset.id, query=search.query, limit=limit, id_from=id_from
        )

    def get_dataset_schema(self, dataset: DatasetDB) -> Dict[str, Any]:
        """Return inner elasticsearch index configuration"""
        schema = self._es.get_schema(id=dataset.id)
        return schema

    async def delete_records_by_query(
        self,
        dataset: DatasetDB,
        query: Optional[BackendRecordsQuery] = None,
    ) -> Tuple[int, int]:
        total, deleted = await self._es.delete_records_by_query(
            id=dataset.id, query=query
        )
        return total, deleted

    async def update_records_by_query(
        self,
        dataset: DatasetDB,
        query: Optional[BackendRecordsQuery] = None,
        **content,
    ) -> Tuple[int, int]:
        total, updated = await self._es.update_records_content(
            id=dataset.id, content=content, query=query
        )
        return total, updated
