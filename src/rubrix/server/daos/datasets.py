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
import json
from typing import Any, Dict, List, Optional, Type

from fastapi import Depends

from rubrix.server.backend.elasticsearch import ElasticsearchBackend
from rubrix.server.backend.mappings.datasets import (
    DATASETS_INDEX_NAME,
    DATASETS_INDEX_TEMPLATE,
)
from rubrix.server.backend.search.model import DatasetsQuery
from rubrix.server.daos.models.datasets import BaseDatasetDB, DatasetDB, SettingsDB
from rubrix.server.daos.records import DatasetRecordsDAO, dataset_records_index
from rubrix.server.errors import WrongTaskError

NO_WORKSPACE = ""
MAX_NUMBER_OF_LISTED_DATASETS = 2500


class DatasetsDAO:
    """Datasets DAO"""

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        es: ElasticsearchBackend = Depends(ElasticsearchBackend.get_instance),
        records_dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
    ) -> "DatasetsDAO":
        """
        Gets or creates the dao instance

        Parameters
        ----------
        es:
            The elasticsearch wrapper dependency

        records_dao:
            The dataset records dao

        Returns
        -------
            The dao instance

        """
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(es, records_dao)
        return cls._INSTANCE

    def __init__(self, es: ElasticsearchBackend, records_dao: DatasetRecordsDAO):
        self._es = es
        self.__records_dao__ = records_dao
        self.init()

    def init(self):
        """Initializes dataset dao. Used on app startup"""
        self._es.create_index_template(
            name=DATASETS_INDEX_NAME,
            template=DATASETS_INDEX_TEMPLATE,
            force_recreate=True,
        )
        self._es.create_index(DATASETS_INDEX_NAME)

    def list_datasets(
        self,
        owner_list: List[str] = None,
        task2dataset_map: Dict[str, Type[BaseDatasetDB]] = None,
    ) -> List[BaseDatasetDB]:

        query = DatasetsQuery(
            owners=owner_list,
            include_no_owner=NO_WORKSPACE in owner_list,
            tasks=[task for task in task2dataset_map] if task2dataset_map else None,
        )

        es_query = self._es.query_builder.map_2_es_query(query=query)
        docs = self._es.list_documents(
            index=DATASETS_INDEX_NAME,
            # TODO(@frascuchon): include id as part of the document as keyword to enable sorting by id
            size=MAX_NUMBER_OF_LISTED_DATASETS,
            query=es_query
        )

        task2dataset_map = task2dataset_map or {}
        return [
            self._es_doc_to_instance(
                doc, ds_class=task2dataset_map.get(task, DatasetDB)
            )
            for doc in docs
            for task in [self.__get_doc_field__(doc, "task")]
        ]

    def create_dataset(self, dataset: BaseDatasetDB) -> BaseDatasetDB:
        """
        Stores a dataset in elasticsearch and creates corresponding dataset records index

        Parameters
        ----------
        dataset:
            The dataset

        Returns
        -------
            Created dataset
        """

        self._es.add_document(
            index=DATASETS_INDEX_NAME,
            doc_id=dataset.id,
            document=self._dataset_to_es_doc(dataset),
        )
        self.__records_dao__.create_dataset_index(dataset, force_recreate=True)
        return dataset

    def update_dataset(
        self,
        dataset: BaseDatasetDB,
    ) -> BaseDatasetDB:
        """
        Updates an stored dataset

        Parameters
        ----------
        dataset:
            The dataset

        Returns
        -------
            The updated dataset

        """
        dataset_id = dataset.id

        self._es.update_document(
            index=DATASETS_INDEX_NAME,
            doc_id=dataset_id,
            document=self._dataset_to_es_doc(dataset),
            partial_update=True,
        )
        return dataset

    def delete_dataset(self, dataset: BaseDatasetDB):
        """
        Deletes indices related to provided dataset

        Parameters
        ----------
        dataset:
            The dataset

        """
        try:
            self._es.delete_index(dataset_records_index(dataset.id))
        finally:
            self._es.delete_document(index=DATASETS_INDEX_NAME, doc_id=dataset.id)

    def find_by_name(
        self,
        name: str,
        owner: Optional[str],
        as_dataset_class: Type[BaseDatasetDB] = DatasetDB,
        task: Optional[str] = None,
    ) -> Optional[BaseDatasetDB]:
        """
        Finds a dataset by name

        Parameters
        ----------
        name: The dataset name
        owner: The dataset owner
        as_dataset_class: The dataset class used to return data
        task: The dataset task string definition

        Returns
        -------
            The found dataset if any. None otherwise
        """
        dataset_id = DatasetDB.build_dataset_id(
            name=name,
            owner=owner,
        )
        document = self._es.get_document_by_id(
            index=DATASETS_INDEX_NAME, doc_id=dataset_id
        )
        if not document and owner is None:
            # We must search by name since we have no owner
            results = self._es.list_documents(
                index=DATASETS_INDEX_NAME,
                query={"query": {"term": {"name.keyword": name}}},
                fetch_once=True,
            )
            results = list(results)
            if len(results) == 0:
                return None

            if len(results) > 1:
                raise ValueError(
                    f"Ambiguous dataset info found for name {name}. Please provide a valid owner"
                )

            document = results[0]

        if document is None:
            return None

        base_ds = self._es_doc_to_instance(document)
        if task and task != base_ds.task:
            raise WrongTaskError(
                detail=f"Provided task {task} cannot be applied to dataset"
            )
        dataset_type = as_dataset_class or DatasetDB
        return self._es_doc_to_instance(document, ds_class=dataset_type)

    @staticmethod
    def _es_doc_to_instance(
        doc: Dict[str, Any], ds_class: Type[BaseDatasetDB] = DatasetDB
    ) -> BaseDatasetDB:
        """Transforms a stored elasticsearch document into a `DatasetDB`"""

        def __key_value_list_to_dict__(
            key_value_list: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            return {data["key"]: json.loads(data["value"]) for data in key_value_list}

        source = doc["_source"]
        tags = source.get("tags", [])
        metadata = source.get("metadata", [])

        data = {
            **source,
            "tags": __key_value_list_to_dict__(tags),
            "metadata": __key_value_list_to_dict__(metadata),
        }

        return ds_class.parse_obj(data)

    @staticmethod
    def _dataset_to_es_doc(dataset: DatasetDB) -> Dict[str, Any]:
        def __dict_to_key_value_list__(data: Dict[str, Any]) -> List[Dict[str, Any]]:
            return [
                {"key": key, "value": json.dumps(value)} for key, value in data.items()
            ]

        data = dataset.dict(by_alias=True)
        tags = data.get("tags", {})
        metadata = data.get("metadata", {})

        return {
            **data,
            "tags": __dict_to_key_value_list__(tags),
            "metadata": __dict_to_key_value_list__(metadata),
        }

    def copy(self, source: DatasetDB, target: DatasetDB):
        source_doc = self._es.get_document_by_id(
            index=DATASETS_INDEX_NAME, doc_id=source.id
        )
        self._es.add_document(
            index=DATASETS_INDEX_NAME,
            doc_id=target.id,
            document={
                **source_doc["_source"],  # we copy extended fields from source document
                **self._dataset_to_es_doc(target),
            },
        )
        index_from = dataset_records_index(source.id)
        index_to = dataset_records_index(target.id)
        self._es.clone_index(index=index_from, clone_to=index_to)

    def close(self, dataset: DatasetDB):
        """Close a dataset. It's mean that release all related resources, like elasticsearch index"""
        self._es.close_index(dataset_records_index(dataset.id))

    def open(self, dataset: DatasetDB):
        """Make available a dataset"""
        self._es.open_index(dataset_records_index(dataset.id))

    def get_all_workspaces(self) -> List[str]:
        """Get all datasets (Only for super users)"""

        metric_data = self._es.compute_metric(
            DATASETS_INDEX_NAME,
            metric_id="all_rubrix_workspaces",
        )
        return [k for k in metric_data]

    def save_settings(self, dataset: DatasetDB, settings: SettingsDB) -> SettingsDB:
        self._es.update_document(
            index=DATASETS_INDEX_NAME,
            doc_id=dataset.id,
            document={"settings": settings.dict(exclude_none=True)},
            partial_update=True,
        )
        return settings

    def load_settings(
        self, dataset: DatasetDB, as_class: Type[SettingsDB]
    ) -> Optional[SettingsDB]:
        doc = self._es.get_document_by_id(index=DATASETS_INDEX_NAME, doc_id=dataset.id)
        if doc:
            settings = self.__get_doc_field__(doc, field="settings")
            return as_class.parse_obj(settings) if settings else None

    def delete_settings(self, dataset: DatasetDB):
        self._es.update_document(
            index=DATASETS_INDEX_NAME,
            doc_id=dataset.id,
            script='ctx._source.remove("settings")',
            partial_update=True,
        )

    def __get_doc_field__(self, doc: Dict[str, Any], field: str) -> Optional[Any]:
        return doc["_source"].get(field)
