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

from argilla.server.daos.backend import BaseDatasetsQuery, GenericElasticEngineBackend
from argilla.server.daos.models.datasets import (
    BaseDatasetDB,
    BaseDatasetSettingsDB,
    DatasetDB,
    DatasetSettingsDB,
    EmbeddingsConfig,
)
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.errors import WrongTaskError


class DatasetsDAO:
    """Datasets DAO"""

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        es: GenericElasticEngineBackend = Depends(GenericElasticEngineBackend.get_instance),
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

    def __init__(
        self,
        es: GenericElasticEngineBackend,
        records_dao: DatasetRecordsDAO,
    ):
        self._es = es
        self.__records_dao__ = records_dao
        self.init()

    def init(self):
        """Initializes dataset dao. Used on app startup"""
        self._es.create_datasets_index()

    def list_datasets(
        self,
        workspaces: List[str] = None,
        task2dataset_map: Dict[str, Type[DatasetDB]] = None,
        name: Optional[str] = None,
    ) -> List[DatasetDB]:
        if not workspaces:
            return []

        query = BaseDatasetsQuery(
            workspaces=workspaces,
            tasks=[task for task in task2dataset_map] if task2dataset_map else None,
            name=name,
        )

        docs = self._es.list_datasets(query)
        task2dataset_map = task2dataset_map or {}
        return [
            self._es_doc_to_instance(
                doc=doc,
                ds_class=task2dataset_map.get(doc["task"], BaseDatasetDB),
            )
            for doc in docs
        ]

    def create_dataset(self, dataset: DatasetDB) -> DatasetDB:
        self._es.add_dataset_document(
            id=dataset.id,
            document=self._dataset_to_es_doc(dataset),
        )
        self._es.create_dataset(
            id=dataset.id,
            task=dataset.task,
            force_recreate=True,
        )
        return dataset

    def update_dataset(
        self,
        dataset: DatasetDB,
    ) -> DatasetDB:
        self._es.update_dataset_document(id=dataset.id, document=self._dataset_to_es_doc(dataset))
        return dataset

    def delete_dataset(self, dataset: DatasetDB):
        self._es.delete(dataset.id)

    def find_by_name_and_workspace(self, name: str, workspace: str) -> Optional[DatasetDB]:
        return self.find_by_name(name=name, workspace=workspace)

    def find_by_name(
        self,
        name: str,
        workspace: str,
        as_dataset_class: Type[DatasetDB] = BaseDatasetDB,
    ) -> Optional[DatasetDB]:
        dataset_id = BaseDatasetDB.build_dataset_id(name=name, workspace=workspace)
        document = self._es.find_dataset(id=dataset_id)
        if document is None:
            return None
        dataset_type = as_dataset_class or BaseDatasetDB
        return self._es_doc_to_instance(document, ds_class=dataset_type)

    @staticmethod
    def _es_doc_to_instance(
        doc: Dict[str, Any],
        ds_class: Type[DatasetDB] = BaseDatasetDB,
    ) -> DatasetDB:
        """Transforms a stored elasticsearch document into a `BaseDatasetDB`"""

        def key_value_list_to_dict(key_value_list: List[Dict[str, Any]]) -> Dict[str, Any]:
            return {data["key"]: json.loads(data["value"]) for data in key_value_list}

        tags = doc.get("tags", [])
        metadata = doc.get("metadata", [])

        data = {
            **doc,
            "tags": key_value_list_to_dict(tags),
            "metadata": key_value_list_to_dict(metadata),
        }

        return ds_class.parse_obj(data)

    @staticmethod
    def _dataset_to_es_doc(dataset: DatasetDB) -> Dict[str, Any]:
        def dict_to_key_value_list(data: Dict[str, Any]) -> List[Dict[str, Any]]:
            return [{"key": key, "value": json.dumps(value)} for key, value in data.items()]

        data = dataset.dict(by_alias=True)
        tags = data.get("tags", {})
        metadata = data.get("metadata", {})

        return {
            **data,
            "tags": dict_to_key_value_list(tags),
            "metadata": dict_to_key_value_list(metadata),
        }

    def copy(self, source: DatasetDB, target: DatasetDB):
        document = self._es.find_dataset(id=source.id)
        self._es.add_dataset_document(
            id=target.id,
            document={
                **document,  # we copy extended fields from source document
                **self._dataset_to_es_doc(target),
            },
        )
        self._es.copy(id_from=source.id, id_to=target.id)

    def open(self, dataset: DatasetDB):
        """Make available a dataset"""
        self._es.open(dataset.id)

    def close(self, dataset: DatasetDB):
        """Close a dataset. It's mean that release all related resources, like elasticsearch index"""
        self._es.close(dataset.id)

    def save_settings(
        self,
        dataset: DatasetDB,
        settings: DatasetSettingsDB,
    ) -> BaseDatasetSettingsDB:
        self._configure_vectors(dataset, settings)
        self._es.update_dataset_document(
            id=dataset.id,
            document={"settings": settings.dict(exclude_none=True)},
        )
        return settings

    def _configure_vectors(self, dataset, settings):
        if not settings.vectors:
            return
        vectors_cfg = {k: v.dim if isinstance(v, EmbeddingsConfig) else int(v) for k, v in settings.vectors.items()}
        self._es.create_dataset(
            id=dataset.id,
            task=dataset.task,
            vectors_cfg=vectors_cfg,
        )

    def load_settings(self, dataset: DatasetDB, as_class: Type[DatasetSettingsDB]) -> Optional[DatasetSettingsDB]:
        doc = self._es.find_dataset(id=dataset.id)
        if doc and "settings" in doc:
            settings = doc["settings"]
            return as_class.parse_obj(settings) if settings else None

    def delete_settings(self, dataset: DatasetDB):
        self._es.remove_dataset_field(
            id=dataset.id,
            field="settings",
        )
