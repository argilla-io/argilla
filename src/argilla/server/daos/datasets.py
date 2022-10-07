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

from argilla.server.daos.backend.elasticsearch import ElasticsearchBackend
from argilla.server.daos.backend.search.model import BaseDatasetsQuery
from argilla.server.daos.models.datasets import (
    BaseDatasetDB,
    BaseDatasetSettingsDB,
    DatasetDB,
    DatasetSettingsDB,
)
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.errors import WrongTaskError

NO_WORKSPACE = ""


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
        self._es.create_datasets_index()

    def list_datasets(
        self,
        owner_list: List[str] = None,
        task2dataset_map: Dict[str, Type[DatasetDB]] = None,
        name: Optional[str] = None,
    ) -> List[DatasetDB]:
        owner_list = owner_list or []
        query = BaseDatasetsQuery(
            owners=owner_list,
            include_no_owner=NO_WORKSPACE in owner_list,
            tasks=[task for task in task2dataset_map] if task2dataset_map else None,
            name=name,
        )

        docs = self._es.list_datasets(query)
        task2dataset_map = task2dataset_map or {}
        return [
            self._es_doc_to_instance(
                doc, ds_class=task2dataset_map.get(task, BaseDatasetDB)
            )
            for doc in docs
            for task in [self.__get_doc_field__(doc, "task")]
        ]

    def create_dataset(self, dataset: DatasetDB) -> DatasetDB:
        self._es.add_dataset_document(
            id=dataset.id, document=self._dataset_to_es_doc(dataset)
        )
        self._es.create_dataset_index(
            id=dataset.id,
            task=dataset.task,
            force_recreate=True,
        )
        return dataset

    def update_dataset(
        self,
        dataset: DatasetDB,
    ) -> DatasetDB:

        self._es.update_dataset_document(
            id=dataset.id, document=self._dataset_to_es_doc(dataset)
        )
        return dataset

    def delete_dataset(self, dataset: DatasetDB):
        self._es.delete(dataset.id)

    def find_by_name(
        self,
        name: str,
        owner: Optional[str],
        as_dataset_class: Type[DatasetDB] = BaseDatasetDB,
        task: Optional[str] = None,
    ) -> Optional[DatasetDB]:

        dataset_id = BaseDatasetDB.build_dataset_id(
            name=name,
            owner=owner,
        )
        document = self._es.find_dataset(id=dataset_id, name=name, owner=owner)
        if document is None:
            return None
        base_ds = self._es_doc_to_instance(document)
        if task and task != base_ds.task:
            raise WrongTaskError(
                detail=f"Provided task {task} cannot be applied to dataset"
            )
        dataset_type = as_dataset_class or BaseDatasetDB
        return self._es_doc_to_instance(document, ds_class=dataset_type)

    @staticmethod
    def _es_doc_to_instance(
        doc: Dict[str, Any], ds_class: Type[DatasetDB] = BaseDatasetDB
    ) -> DatasetDB:
        """Transforms a stored elasticsearch document into a `BaseDatasetDB`"""

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
        source_doc = self._es.find_dataset(id=source.id)
        self._es.add_dataset_document(
            id=target.id,
            document={
                **source_doc["_source"],  # we copy extended fields from source document
                **self._dataset_to_es_doc(target),
            },
        )
        self._es.copy(id_from=source.id, id_to=target.id)

    def close(self, dataset: DatasetDB):
        """Close a dataset. It's mean that release all related resources, like elasticsearch index"""
        self._es.close(dataset.id)

    def open(self, dataset: DatasetDB):
        """Make available a dataset"""
        self._es.open(dataset.id)

    def get_all_workspaces(self) -> List[str]:
        """Get all datasets (Only for super users)"""
        metric_data = self._es.compute_argilla_metric(
            metric_id="all_argilla_workspaces"
        )
        return [k for k in metric_data]

    def save_settings(
        self, dataset: DatasetDB, settings: DatasetSettingsDB
    ) -> BaseDatasetSettingsDB:
        self._es.update_dataset_document(
            id=dataset.id, document={"settings": settings.dict(exclude_none=True)}
        )
        return settings

    def load_settings(
        self, dataset: DatasetDB, as_class: Type[DatasetSettingsDB]
    ) -> Optional[DatasetSettingsDB]:
        doc = self._es.find_dataset(id=dataset.id)
        if doc:
            settings = self.__get_doc_field__(doc, field="settings")
            return as_class.parse_obj(settings) if settings else None

    def delete_settings(self, dataset: DatasetDB):
        self._es.remove_dataset_field(dataset.id, field="settings")

    def __get_doc_field__(self, doc: Dict[str, Any], field: str) -> Optional[Any]:
        return doc["_source"].get(field)
