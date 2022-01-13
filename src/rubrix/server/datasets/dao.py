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
from typing import Any, Dict, List, Optional, Type, TypeVar

import deprecated
from fastapi import Depends

from rubrix.server.commons.es_wrapper import ElasticsearchWrapper, create_es_wrapper
from rubrix.server.tasks.commons import TaskType

from ..commons.es_settings import (
    DATASETS_INDEX_NAME,
    DATASETS_INDEX_TEMPLATE,
    DATASETS_RECORDS_INDEX_NAME,
)
from .model import DatasetDB


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


BaseDatasetDB = TypeVar("BaseDatasetDB", bound=DatasetDB)


class DatasetsDAO:
    """Datasets DAO"""

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls, es: ElasticsearchWrapper = Depends(create_es_wrapper)
    ) -> "DatasetsDAO":
        """
        Gets or creates the dao instance

        Parameters
        ----------
        es:
            The elasticsearch wrapper dependency

        Returns
        -------
            The dao instance

        """
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(es)
        return cls._INSTANCE

    def __init__(self, es: ElasticsearchWrapper):
        self._es = es
        self.init()

    def init(self):
        """Initializes dataset dao. Used on app startup"""
        self._es.create_index_template(
            name=DATASETS_INDEX_NAME,
            template=DATASETS_INDEX_TEMPLATE,
            force_recreate=True,
        )
        self._es.create_index(DATASETS_INDEX_NAME)

    def list_datasets(self, owner_list: List[str] = None) -> List[DatasetDB]:
        """
        List the dataset for an owner list

        Parameters
        ----------
        owner_list:
            The selected owners. Optional

        Returns
        -------
            A list of datasets for a given owner list, if any. All datasets, otherwise

        """
        query = {}
        if owner_list:
            query = {"query": {"terms": {"owner.keyword": owner_list}}}
        docs = self._es.list_documents(
            index=DATASETS_INDEX_NAME,
            query=query,
        )
        return [self._es_doc_to_dataset(doc) for doc in docs]

    def create_dataset(self, dataset: DatasetDB) -> DatasetDB:
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

        self._es.create_index(
            index=dataset_records_index(dataset.id),
            force_recreate=True,
        )
        return dataset

    def update_dataset(
        self,
        dataset: DatasetDB,
    ) -> DatasetDB:
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

    def delete_dataset(self, dataset: DatasetDB):
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

    def find_by_id(
        self, dataset_id: str, ds_class: Type[BaseDatasetDB] = DatasetDB
    ) -> Optional[BaseDatasetDB]:
        """
        Finds a dataset db by its id

        Parameters
        ----------
        dataset_id:
            The dataset id
        ds_class:
            Class used for data deserialization. Class could be an specialization
            of DatasetDB. Default ``DatasetDB``

        Returns
        -------
            The dataset instance if found. ``None`` otherwise
        """
        document = self._es.get_document_by_id(
            index=DATASETS_INDEX_NAME, doc_id=dataset_id
        )
        if document:
            return self._es_doc_to_dataset(document, ds_class=ds_class)

    def find_by_name(self, name: str, owner: Optional[str]) -> Optional[DatasetDB]:
        """
        Finds a dataset by name

        Parameters
        ----------
        name:
            The dataset name
        owner:
            The dataset owner

        Returns
        -------
            The found dataset if any. None otherwise
        """
        dataset = DatasetDB(name=name, owner=owner, task=TaskType.text_classification)
        document = self._es.get_document_by_id(
            index=DATASETS_INDEX_NAME, doc_id=dataset.id
        )
        if not document and owner is None:
            # We must search by name since we have no owner
            results = self._es.list_documents(
                index=DATASETS_INDEX_NAME,
                query={"query": {"term": {"name.keyword": name}}},
            )
            results = list(results)
            if len(results) == 0:
                return None

            if len(results) > 1:
                raise ValueError(
                    f"Ambiguous dataset info found for name {name}. Please provide a valid owner"
                )

            document = results[0]
        return self._es_doc_to_dataset(document) if document else None

    @staticmethod
    def _es_doc_to_dataset(
        doc: Dict[str, Any], ds_class: Type[BaseDatasetDB] = DatasetDB
    ) -> BaseDatasetDB:
        """Transforms a stored elasticsearch document into a `DatasetDB`"""

        def __key_value_list_to_dict__(
            key_value_list: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            return {data["key"]: json.loads(data["value"]) for data in key_value_list}

        source = doc["_source"]
        tags = source.pop("tags", [])
        metadata = source.pop("metadata", [])

        return ds_class.parse_obj(
            {
                **source,
                "tags": __key_value_list_to_dict__(tags),
                "metadata": __key_value_list_to_dict__(metadata),
            }
        )

    @staticmethod
    def _dataset_to_es_doc(dataset: DatasetDB) -> Dict[str, Any]:
        def __dict_to_key_value_list__(data: Dict[str, Any]) -> List[Dict[str, Any]]:
            return [
                {"key": key, "value": json.dumps(value)} for key, value in data.items()
            ]

        data = dataset.dict(by_alias=True)
        tags = data.pop("tags", {})
        metadata = data.pop("metadata", {})

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


_instance: Optional[DatasetsDAO] = None


@deprecated.deprecated(reason="Use ``DatasetsDAO.get_instance`` class method instead")
def create_datasets_dao(
    es: ElasticsearchWrapper = Depends(create_es_wrapper),
) -> DatasetsDAO:
    """
    Creates the dao
    Parameters
    ----------
    es:
        The elasticsearch wrapper dependency>

    Returns
    -------
        The dao instance

    """
    global _instance
    if _instance is None:
        _instance = DatasetsDAO(es)
    return _instance
