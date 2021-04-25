import os
from typing import Any, Callable, Dict, Iterable, List, Optional

import elasticsearch
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk as es_bulk, scan as es_scan
from rubrix.logging import LoggingMixin

try:
    import ujson as json
except ModuleNotFoundError:
    import json


from .settings import settings


class ElasticsearchWrapper(LoggingMixin):
    """A simple elasticsearch client wrapper for atomize some repetitive operations"""

    def __init__(self, es_client: Elasticsearch):
        self.__client__ = es_client

    @property
    def client(self):
        """The elasticsearch client"""
        return self.__client__

    def list_documents(
        self, index: str, query: Dict[str, Any] = None
    ) -> Iterable[Dict[str, Any]]:
        """
        List ALL documents of an elasticsearch index
        Parameters
        ----------
        index:
            The index name
        query:
            The es query for filter results. Default: None

        Returns
        -------
        A sequence of documents resulting from applying the query on the index

        """
        return es_scan(self.__client__, query=query or {}, index=index)

    def index_exists(self, index: str) -> bool:
        """
        Checks if provided index exists

        Parameters
        ----------
        index:
            The index name

        Returns
        -------
            True if index exists. False otherwise
        """
        return self.__client__.indices.exists(index)

    def search(
        self,
        index: str,
        routing: str = None,
        size: int = 100,
        query: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Apply a search over a index.
        See <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html>

        Parameters
        ----------
        index:
            The index name
        routing:
            The routing key. Optional
        size:
            Number of results to return. Default=100
        query:
            The elasticsearch query. Optional

        Returns
        -------

        """
        return self.__client__.search(
            index=index,
            body=query or {},
            routing=routing,
            track_total_hits=True,
            rest_total_hits_as_int=True,
            size=size,
        )

    def create_index(
        self, index: str, force_recreate: bool = False, mappings: Dict[str, Any] = None
    ):
        """
        Applies a index creation with provided mapping configuration.

        See <https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html>

        Parameters
        ----------
        index:
            The index name
        force_recreate:
            If True, the index will be recreated (if exists). Default=False
        mappings:
            The mapping configuration. Optional.

        """
        if force_recreate:
            self.delete_index(index)
        if not self.index_exists(index):
            self.__client__.indices.create(
                index=index, body={"mappings": mappings or {}}
            )

    def create_index_template(
        self, name: str, template: Dict[str, Any], force_recreate: bool = False
    ):
        """
        Applies a index template creation with provided template definition.

        Parameters
        ----------
        name:
            The template index name
        template:
            The template definition
        force_recreate:
            If True, the template will be recreated (if exists). Default=False

        """
        if force_recreate or not self.__client__.indices.exists_template(name):
            self.__client__.indices.put_template(name=name, body=template)

    def delete_index(self, index: str):
        """Deletes an elasticsearch index"""
        self.__client__.indices.delete(index, ignore=[400, 404])

    def add_document(self, index: str, doc_id: str, document: Dict[str, Any]):
        """
        Creates/updates a document in a index

        See <http://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html>

        Parameters
        ----------
        index:
            The index name
        doc_id:
            The document id
        document:
            The document source

        """
        self.__client__.index(index=index, body=document, id=doc_id, refresh="wait_for")

    def get_document_by_id(self, index: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its id

        See <https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-get.html>

        Parameters
        ----------
        index:
            The index name
        doc_id:
            The document id

        Returns
        -------
            The elasticsearch document if found, None otherwise
        """
        try:
            return self.__client__.get(index=index, id=doc_id)
        except elasticsearch.exceptions.NotFoundError:
            return None

    def delete_document(self, index: str, doc_id: str):
        """
        Deletes a document from an index.

        See <http://www.elastic.co/guide/en/elasticsearch/reference/current/docs-delete.html>

        Parameters
        ----------
        index:
            The index name
        doc_id:
            The document id

        Returns
        -------

        """
        self.__client__.delete(index=index, id=doc_id)

    def add_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]],
        routing: Callable[[Dict[str, Any]], str] = None,
        doc_id: Callable[[Dict[str, Any]], str] = None,
    ) -> int:
        """
        Adds or updated a set of documents to an index. Documents can contains
        partial information of document.

        See <https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html>

        Parameters
        ----------
        index:
            The index name
        documents:
            The set of documents
        routing:
            The routing key
        doc_id

        Returns
        -------
            The number of failed documents
        """

        def map_doc_2_action(doc: Dict[str, Any]) -> Dict[str, Any]:
            """Configures bulk action"""
            return {
                "_op_type": "update",
                "_index": index,
                "_id": doc_id(doc) if doc_id else doc["_id"],
                "_routing": routing(doc) if routing else None,
                "doc": doc,
                "doc_as_upsert": True,
            }

        success, failed = es_bulk(
            self.__client__,
            index=index,
            actions=map(map_doc_2_action, documents),
            raise_on_error=True,
            refresh="wait_for",
        )
        return len(failed)

    def get_field_mapping(self, index: str, field_name: str) -> Dict[str, str]:
        """
            Returns the mapping for a given field name (can be as wildcard notation). The result
        consist on a dictionary with full field name as key and its type as value

        See <http://www.elastic.co/guide/en/elasticsearch/reference/current/indices-get-field-mapping.html>

        Parameters
        ----------
        index:
            The index name
        field_name:
            The field name pattern

        Returns
        -------
            A dictionary with full field name as key and its type as value
        """
        try:
            response = self.__client__.indices.get_field_mapping(
                fields=field_name,
                index=index,
                ignore_unavailable=False,
            )
            return {
                key: list(definition["mapping"].values())[0]["type"]
                for key, definition in response[index]["mappings"].items()
                if not key.endswith(".raw")  # Drop raw version of fields
            }
        except NotFoundError:
            # No mapping data
            return {}

    def update_document(
        self,
        index: str,
        doc_id: str,
        document: Dict[str, Any],
        partial_update: bool = False,
    ):
        """
        Updates a document in a given index

        Parameters
        ----------
        index:
            The index name
        doc_id:
            The document id
        document:
            The document data. Could be partial document info
        partial_update:
            If True, document contains partial info, and will be
            merged with stored document. If false, the stored document
            will be overwritten. Default=False

        Returns
        -------

        """
        if partial_update:
            self.__client__.update(index=index, id=doc_id, body={"doc": document})
        self.__client__.index(index=index, id=doc_id, body=document)

    def open_index(self, index: str):
        """
        Open an elasticsearch index. If index is already open, this operation will do nothing

        See `<https://www.elastic.co/guide/en/elasticsearch/reference/7.11/indices-open-close.html>`_

        Parameters
        ----------
        index:
            The index name
        """
        self.__client__.indices.open(
            index=index, wait_for_active_shards=settings.es_records_index_shards
        )

    def close_index(self, index: str):
        """
        Closes an elasticsearch index. If index is already closed, this operation will do nothing.

        See `<https://www.elastic.co/guide/en/elasticsearch/reference/7.11/indices-open-close.html>`_

        Parameters
        ----------
        index:
            The index name
        """
        self.__client__.indices.close(
            index=index,
            ignore_unavailable=True,
            wait_for_active_shards=settings.es_records_index_shards,
        )


_instance = None  # The singleton instance


def create_es_wrapper() -> ElasticsearchWrapper:
    """
        Creates a instance of ElasticsearchWrapper.

    This function is used in fastapi for resolve component dependencies.

    See <https://fastapi.tiangolo.com/tutorial/dependencies/>

    Returns
    -------

    """

    global _instance
    if _instance is None:
        es_client = Elasticsearch(hosts=settings.elasticsearch)
        _instance = ElasticsearchWrapper(es_client)

    return _instance
