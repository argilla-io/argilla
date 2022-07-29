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

from typing import Any, Callable, Dict, Iterable, List, Optional

import deprecated
from opensearchpy import NotFoundError, OpenSearch, OpenSearchException, RequestError
from opensearchpy.helpers import bulk as es_bulk
from opensearchpy.helpers import scan as es_scan

from rubrix.logging import LoggingMixin
from rubrix.server.commons.models import TaskType
from rubrix.server.elasticseach import query_helpers
from rubrix.server.elasticseach.mappings.text2text import text2text_mappings
from rubrix.server.elasticseach.mappings.text_classification import (
    text_classification_mappings,
)
from rubrix.server.elasticseach.mappings.token_classification import (
    token_classification_mappings,
)
from rubrix.server.elasticseach.metrics import ALL_METRICS
from rubrix.server.elasticseach.metrics.base import ElasticsearchMetric
from rubrix.server.elasticseach.search.query_builder import EsQueryBuilder
from rubrix.server.errors import EntityNotFoundError, InvalidTextSearchError

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from rubrix.server.settings import settings


class ClosedIndexError(Exception):
    pass


class IndexNotFoundError(Exception):
    pass


class GenericSearchError(Exception):
    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error


class backend_error_handler:
    def __init__(self, index: str):
        # Maybe a backend to detect the backend nature...
        self._index = index

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        if not exception_value:
            return
        try:
            raise exception_value from exception_value
        except RequestError as ex:
            if ex.error == "search_phase_execution_exception":
                detail = exception_value.info["error"]
                detail = detail.get("root_cause")
                detail = detail[0].get("reason") if detail else ex.info["error"]

                raise InvalidTextSearchError(detail)
            elif ex.error == "index_closed_exception":
                raise ClosedIndexError(self._index)
            raise GenericSearchError(exception_value) from exception_value
        except NotFoundError as ex:
            raise IndexNotFoundError(ex)
        except OpenSearchException as ex:
            raise GenericSearchError(ex)


class ElasticsearchBackend(LoggingMixin):
    """
    Encapsulates logic about the communication, queries and index mapping
    transformations between DAOs layer and the elasticsearch backend.
    """

    _INSTANCE = None

    @classmethod
    def get_instance(cls) -> "ElasticsearchBackend":
        """
        Creates an instance of ElasticsearchBackend.

        This function is used in fastapi for resolve component dependencies.

        See <https://fastapi.tiangolo.com/tutorial/dependencies/>

        Returns
        -------

        """

        if cls._INSTANCE is None:
            es_client = OpenSearch(
                hosts=settings.elasticsearch,
                verify_certs=settings.elasticsearch_ssl_verify,
                ca_certs=settings.elasticsearch_ca_path,
                # Extra args to es configuration -> TODO: extensible by settings
                retry_on_timeout=True,
                max_retries=5,
            )
            cls._INSTANCE = cls(
                es_client,
                query_builder=EsQueryBuilder(),
                metrics={**ALL_METRICS},
                mappings={
                    TaskType.text_classification: text_classification_mappings(),
                    TaskType.token_classification: token_classification_mappings(),
                    TaskType.text2text: text2text_mappings(),
                },
            )

        return cls._INSTANCE

    def __init__(
        self,
        es_client: OpenSearch,
        query_builder: EsQueryBuilder,
        metrics: Dict[str, ElasticsearchMetric] = None,
        mappings: Dict[str, Dict[str, Any]] = None,
    ):
        self.__client__ = es_client
        self.__query_builder__ = query_builder
        self.__defined_metrics__ = metrics or {}
        self.__tasks_mappings__ = mappings

    @property
    def client(self):
        """The elasticsearch client"""
        return self.__client__

    @property
    def query_builder(self):
        """The query builder"""
        return self.__query_builder__

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
        with backend_error_handler(index=index):
            return self.__client__.search(
                index=index,
                body=query or {},
                routing=routing,
                track_total_hits=True,
                rest_total_hits_as_int=True,
                size=size,
            )

    def create_index(
        self,
        index: str,
        force_recreate: bool = False,
        settings: Dict[str, Any] = None,
        mappings: Dict[str, Any] = None,
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
        settings:
            The index settings configuration
        mappings:
            The mapping configuration. Optional.

        """
        with backend_error_handler(index):
            if force_recreate:
                self.delete_index(index)
            if not self.index_exists(index):
                self.__client__.indices.create(
                    index=index,
                    body={"settings": settings or {}, "mappings": mappings or {}},
                    ignore=400,
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
        with backend_error_handler(index=""):
            if force_recreate or not self.__client__.indices.exists_template(name):
                self.__client__.indices.put_template(name=name, body=template)

    def delete_index_template(self, index_template: str):
        """Deletes an index template"""
        with backend_error_handler(index=""):

            if self.__client__.indices.exists_index_template(index_template):
                self.__client__.indices.delete_template(
                    name=index_template, ignore=[400, 404]
                )

    def delete_index(self, index: str):
        """Deletes an elasticsearch index"""
        with backend_error_handler(index=index):
            if self.index_exists(index):
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
        with backend_error_handler(index=index):
            self.__client__.index(
                index=index, body=document, id=doc_id, refresh="wait_for"
            )

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
            if self.__client__.exists(index=index, id=doc_id):
                return self.__client__.get(index=index, id=doc_id)
        except NotFoundError:
            return None
        except Exception as ex:
            with backend_error_handler(index=index):
                raise ex

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
        with backend_error_handler(index=index):
            if self.__client__.exists(index=index, id=doc_id):
                self.__client__.delete(index=index, id=doc_id, refresh=True)

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
            data = {
                "_op_type": "index",
                "_index": index,
                "_routing": routing(doc) if routing else None,
                **doc,
            }

            _id = doc_id(doc) if doc_id else None
            if _id is not None:
                data["_id"] = _id

            return data

        with backend_error_handler(index=index):
            success, failed = es_bulk(
                self.__client__,
                index=index,
                actions=map(map_doc_2_action, documents),
                raise_on_error=True,
                refresh="wait_for",
            )
            return len(failed)

    def get_mapping(self, index: str) -> Dict[str, Any]:
        """
        Return the configured index mapping

        See `<https://www.elastic.co/guide/en/elasticsearch/reference/7.13/indices-get-mapping.html>`

        """
        try:
            response = self.__client__.indices.get_mapping(
                index=index,
                ignore_unavailable=False,
                include_type_name=True,
            )
            return list(response[index]["mappings"].values())[0]["properties"]
        except NotFoundError:
            return {}
        except Exception as ex:
            with backend_error_handler(index=index):
                raise ex

    def get_field_mapping(
        self, index: str, field_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
            Returns the mapping for a given field name (can be as wildcard notation). The result
        consist on a dictionary with full field name as key and its type as value

        See <http://www.elastic.co/guide/en/elasticsearch/reference/7.13/indices-get-field-mapping.html>

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
                fields=field_name or "*",
                index=index,
                ignore_unavailable=False,
            )
            return {
                key: list(definition["mapping"].values())[0]["type"]
                for key, definition in response[index]["mappings"].items()
            }
        except NotFoundError:
            # No mapping data
            return {}
        except Exception as ex:
            with backend_error_handler(index=index):
                raise ex

    def update_document(
        self,
        index: str,
        doc_id: str,
        document: Optional[Dict[str, Any]] = None,
        script: Optional[str] = None,
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
        # TODO: validate either doc or script are provided
        with backend_error_handler(index=index):
            if not partial_update:
                return self.__client__.index(
                    index=index, id=doc_id, body=document, refresh=True
                )

            body = {"script": script} if script else {"doc": document}
            return self.__client__.update(
                index=index,
                id=doc_id,
                body=body,
                refresh=True,
                retry_on_conflict=500,  # TODO: configurable
            )

    def open_index(self, index: str):
        """
        Open an elasticsearch index. If index is already open, this operation will do nothing

        See `<https://www.elastic.co/guide/en/elasticsearch/reference/7.11/indices-open-close.html>`_

        Parameters
        ----------
        index:
            The index name
        """
        with backend_error_handler(index=index):
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
        with backend_error_handler(index=index):
            self.__client__.indices.close(
                index=index,
                ignore_unavailable=True,
                wait_for_active_shards=settings.es_records_index_shards,
            )

    def clone_index(self, index: str, clone_to: str, override: bool = True):
        """
        Clone an existing index. During index clone, source must be setup as read-only index. Then, changes can be
        applied

        See `<https://www.elastic.co/guide/en/elasticsearch/reference/7.x/indices-clone-index.html>`_

        Parameters
        ----------
        index:
            The source index name
        clone_to:
            The destination index name
        override:
            If True, destination index will be removed if exists
        """
        with backend_error_handler(index=index):
            try:
                index_read_only = self.is_index_read_only(index)
                if not index_read_only:
                    self.index_read_only(index, read_only=True)
                if override:
                    self.delete_index(clone_to)
                self.__client__.indices.clone(
                    index=index,
                    target=clone_to,
                    wait_for_active_shards=settings.es_records_index_shards,
                )
            finally:
                self.index_read_only(index, read_only=index_read_only)
                self.index_read_only(clone_to, read_only=index_read_only)

    def is_index_read_only(self, index: str) -> bool:
        """
        Fetch info about read-only configuration index

        Parameters
        ----------
        index:
            The index name

        Returns
        -------
            True if queried index is read-only, False otherwise

        """
        with backend_error_handler(index=index):
            response = self.__client__.indices.get_settings(
                index=index,
                name="index.blocks.write",
                allow_no_indices=True,
                flat_settings=True,
            )
            return (
                response[index]["settings"]["index.blocks.write"] == "true"
                if response
                else False
            )

    def index_read_only(self, index: str, read_only: bool):
        """
        Enable/disable index read only

        Parameters
        ----------
        index:
            The index name
        read_only:
            True for enable read-only, False otherwise

        """
        with backend_error_handler(index=index):
            self.__client__.indices.put_settings(
                index=index,
                body={"settings": {"index.blocks.write": read_only}},
                ignore=404,
            )

    def create_field_mapping(
        self,
        index: str,
        field_name: str,
        mapping: Dict[str, Any],
    ):
        """Creates or updates an index field mapping configuration"""
        with backend_error_handler(index=index):
            self.__client__.indices.put_mapping(
                index=index,
                body={"properties": {field_name: mapping}},
            )

    def get_cluster_info(self) -> Dict[str, Any]:
        """Returns basic about es cluster"""
        try:
            return self.__client__.info()
        except OpenSearchException as ex:
            return {"error": ex}

    def aggregate(self, index: str, aggregation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an aggregation over the index returning ONLY the agg results"""
        with backend_error_handler(index=index):
            aggregation_name = "aggregation"
            es_query = {"aggs": {aggregation_name: aggregation}}

            results = self.search(index=index, size=0, query=es_query)
            aggs_results = results["aggregations"]
            return query_helpers.parse_aggregations(aggs_results).get(aggregation_name)

    def find_metric_by_id(self, metric_id: str) -> Optional[ElasticsearchMetric]:
        metric = self.__defined_metrics__.get(metric_id)
        if not metric:
            raise EntityNotFoundError(name=metric_id, type=ElasticsearchMetric)
        return metric

    def get_task_mapping(self, task: TaskType) -> Dict[str, Any]:
        return self.__tasks_mappings__[task]

    def compute_metric(
        self,
        index: str,
        metric_id: str,
        query: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        metric = self.find_metric_by_id(metric_id)
        # Only for metadata aggregation. In a future could be nice to provide the whole index schema
        params.update(
            {"schema": self.get_field_mapping(index=index, field_name="metadata.*")}
        )

        filtered_params = {
            argument: params[argument]
            for argument in metric.metric_arg_names
            if argument in params
        }

        aggs = metric.aggregation_request(**filtered_params)
        if not aggs:
            return {}
        if not isinstance(aggs, list):
            aggs = [aggs]
        results = {}
        for agg in aggs:
            es_query = {
                **self.query_builder.map_2_es_query(
                    schema=self.get_index_mapping(index),
                    query=query,
                ),
                "aggs": agg,
            }
            search_result = self.search(index=index, query=es_query, size=0)
            search_aggregations = search_result.get("aggregations", {})

            if search_aggregations:
                parsed_aggregations = query_helpers.parse_aggregations(
                    search_aggregations
                )
                results.update(parsed_aggregations)

        return metric.aggregation_result(results.get(metric_id, results))

    def get_index_mapping(self, index: str) -> Dict[str, Any]:
        with backend_error_handler(index=index):
            response = self.__client__.indices.get_mapping(index=index)
            if index in response:
                response = response.get(index)
            return response


_instance = None  # The singleton instance


@deprecated.deprecated(reason="Use `ElasticsearchBackend.get_instance` instead")
def create_es_wrapper() -> ElasticsearchBackend:
    """
        Creates a instance of ElasticsearchBackend.

    This function is used in fastapi for resolve component dependencies.

    See <https://fastapi.tiangolo.com/tutorial/dependencies/>

    Returns
    -------

    """

    global _instance
    if _instance is None:
        _instance = ElasticsearchBackend.get_instance()

    return _instance
