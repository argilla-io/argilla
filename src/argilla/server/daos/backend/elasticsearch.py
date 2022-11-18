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
import re
import warnings
from typing import Any, Dict, Iterable, List, Optional, Tuple

from opensearchpy import NotFoundError, OpenSearch, OpenSearchException, RequestError
from opensearchpy.exceptions import OpenSearchWarning
from opensearchpy.helpers import bulk as es_bulk
from opensearchpy.helpers import reindex, scan

from argilla.logging import LoggingMixin
from argilla.server.commons.models import TaskType
from argilla.server.daos.backend import query_helpers
from argilla.server.daos.backend.mappings.datasets import (
    DATASETS_INDEX_NAME,
    datasets_index_mappings,
)
from argilla.server.daos.backend.mappings.helpers import (
    mappings,
    tasks_common_mappings,
    tasks_common_settings,
)
from argilla.server.daos.backend.mappings.text2text import text2text_mappings
from argilla.server.daos.backend.mappings.text_classification import (
    text_classification_mappings,
)
from argilla.server.daos.backend.mappings.token_classification import (
    token_classification_mappings,
)
from argilla.server.daos.backend.metrics import ALL_METRICS
from argilla.server.daos.backend.metrics.base import ElasticsearchMetric
from argilla.server.daos.backend.search.model import (
    BackendRecordsQuery,
    BaseDatasetsQuery,
    SortableField,
    SortConfig,
)
from argilla.server.daos.backend.search.query_builder import EsQueryBuilder
from argilla.server.errors import EntityNotFoundError, InvalidTextSearchError
from argilla.server.errors.task_errors import MetadataLimitExceededError

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from argilla.server.settings import settings


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
        # This line disable all open search client warnings
        warnings.filterwarnings("ignore", category=OpenSearchWarning)
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        if not exception_value:
            return
        try:
            raise exception_value from exception_value
        except RequestError as ex:
            detail = self.__get_es_error_detail__(ex, exception_value)
            if ex.error == "search_phase_execution_exception":
                detail = detail or ex.info["error"]
                raise InvalidTextSearchError(detail)
            elif ex.error == "index_closed_exception":
                raise ClosedIndexError(self._index)
            raise GenericSearchError(exception_value) from exception_value
        except NotFoundError as ex:
            raise IndexNotFoundError(ex)
        except OpenSearchException as ex:
            raise GenericSearchError(ex)

    def __get_es_error_detail__(self, ex, exception_value) -> Optional[str]:
        detail = exception_value.info["error"]
        detail = detail.get("root_cause")

        return detail[0].get("reason")


class ElasticsearchBackend(LoggingMixin):
    """
    Encapsulates logic about the communication, queries and index mapping
    transformations between DAOs layer and the elasticsearch backend.
    """

    _INSTANCE = None

    __HIGHLIGHT_PRE_TAG__ = "<@@-ar-key>"
    __HIGHLIGHT_POST_TAG__ = "</@@-ar-key>"
    __HIGHLIGHT_VALUES_REGEX__ = re.compile(
        rf"{__HIGHLIGHT_PRE_TAG__}(.+?){__HIGHLIGHT_POST_TAG__}"
    )

    __HIGHLIGHT_PHRASE_PRE_PARSER_REGEX__ = re.compile(
        rf"{__HIGHLIGHT_POST_TAG__}\s+{__HIGHLIGHT_PRE_TAG__}"
    )

    # TODO(@frascuchon): Once id is included as keyword in datasets index, we can discard this
    __MAX_NUMBER_OF_LISTED_DATASETS__ = 2500

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

    def _list_documents(
        self,
        index: str,
        query: Dict[str, Any] = None,
        sort_cfg: Optional[List[Dict[str, Any]]] = None,
        size: Optional[int] = None,
        fetch_once: bool = False,
    ) -> Iterable[Dict[str, Any]]:
        """
        List ALL documents of an elasticsearch index
        Parameters
        ----------
        index:
            The index name
        sor_id:
            The sort id configuration
        query:
            The es query for filter results. Default: None
        sort_cfg:
            Customized configuration for sort-by id
        size:
            Amount of samples to retrieve per iteration, 1000 by default
        fetch_once:
            If enabled, will return only the `size` first records found. Default to: ``False``

        Returns
        -------
        A sequence of documents resulting from applying the query on the index

        """
        size = size or 1000
        query = query.copy() or {}
        if sort_cfg:
            query["sort"] = sort_cfg
        query["track_total_hits"] = False  # Speedup pagination
        response = self.__client__.search(index=index, body=query, size=size)
        while response["hits"]["hits"]:
            for hit in response["hits"]["hits"]:
                yield hit
            if fetch_once:
                break

            last_id = hit["_id"]
            query["search_after"] = [last_id]
            response = self.__client__.search(index=index, body=query, size=size)

    def _index_exists(self, index: str) -> bool:
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

    def _search(
        self,
        index: str,
        routing: str = None,
        size: int = 100,
        query: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Apply a search over an index.
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

    def _create_index(
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
        force_recreate:
            If True, the index will be recreated (if exists). Default=False
        settings:
            The index settings configuration
        mappings:
            The mapping configuration. Optional.

        """
        with backend_error_handler(index):
            if force_recreate:
                self._delete_index(index)
            if not self._index_exists(index):
                self.__client__.indices.create(
                    index=index,
                    body={"settings": settings or {}, "mappings": mappings or {}},
                    ignore=400,
                )

    def _create_index_template(
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

    def _delete_index(self, index: str, raises_error: bool = False):
        """Deletes an elasticsearch index"""
        with backend_error_handler(index=index):
            if self._index_exists(index):
                ignore_errors = [400, 404]
                if raises_error:
                    ignore_errors = []
                self.__client__.indices.delete(index, ignore=ignore_errors)

    def _add_document(self, index: str, doc_id: str, document: Dict[str, Any]):
        """
        Creates/updates a document in an index

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

    def _get_document_by_id(self, index: str, doc_id: str) -> Optional[Dict[str, Any]]:
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

    def _delete_document(self, index: str, doc_id: str):
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
        id: str,
        documents: List[Dict[str, Any]],
    ) -> int:
        index = dataset_records_index(id)

        def doc_id(r):
            return r.get("id")

        def map_doc_2_action(doc: Dict[str, Any]) -> Dict[str, Any]:
            """Configures bulk action"""
            data = {
                "_op_type": "index",
                "_index": index,
                "_routing": None,  # TODO(@frascuchon): Use a sharding routing
                **doc,
            }

            id_ = doc_id(doc)
            if id_ is not None:
                data["_id"] = id_

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

    def _get_field_mapping(
        self,
        index: str,
        field_name: Optional[str] = None,
        exclude_subfields: bool = False,
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
        exclude_subfields:
            If True, exclude extra subfields from mappings definition

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
            schema = self._extract_index_schema_from_response(
                index=index, es_response=response
            )
            data = {
                key: list(definition["mapping"].values())[0]["type"]
                for key, definition in schema["mappings"].items()
            }

            if exclude_subfields:
                # Remove `text`, `exact` and `wordcloud` fields
                def is_subfield(key: str):
                    for suffix in ["exact", "text", "wordcloud"]:
                        if suffix in key:
                            return True
                    return False

                data = {
                    key: value for key, value in data.items() if not is_subfield(key)
                }

            return data
        except NotFoundError:
            # No mapping data
            return {}
        except Exception as ex:
            with backend_error_handler(index=index):
                raise ex

    def _update_document(
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

    def _close_index(self, index: str):
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

    def _clone_index(self, index: str, clone_to: str, override: bool = True):
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
                    self._delete_index(clone_to)
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

    def _create_field_mapping(
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

            results = self._search(index=index, size=0, query=es_query)
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
        id: str,
        metric_id: str,
        query: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        index = dataset_records_index(id)
        return self._compute_metric(
            index=index,
            metric_id=metric_id,
            query=query,
            schema=self.get_schema(id),
            params=params,
        )

    def get_schema(self, id: str) -> Dict[str, Any]:
        index = dataset_records_index(id)
        with backend_error_handler(index=index):
            response = self.__client__.indices.get_mapping(index=index)
            return self._extract_index_schema_from_response(
                index=index, es_response=response
            )

    async def update_records_content(
        self,
        id: str,
        content: Dict[str, Any],
        query: Optional[BaseDatasetsQuery],
    ) -> Tuple[int, int]:
        index = dataset_records_index(id)
        with backend_error_handler(index=index):
            es_query = self.query_builder.map_2_es_query(
                schema=self.get_schema(id),
                query=query,
            )
            response = self.client.update_by_query(
                index=index,
                body={
                    "query": es_query["query"],
                    "script": {
                        "lang": "painless",
                        "inline": ";".join(
                            [f"ctx._source.{k}='{v}'" for k, v in content.items()]
                        ),
                    },
                },
                slices="auto",
                wait_for_completion=True,
                conflicts="proceed",
            )
            total, updated = response["total"], response["updated"]
            return total, updated

    async def delete_records_by_query(
        self,
        id: str,
        query: Optional[BaseDatasetsQuery],
    ) -> Tuple[int, int]:

        index = dataset_records_index(id)
        with backend_error_handler(index=index):
            es_query = self.query_builder.map_2_es_query(
                schema=self.get_schema(id),
                query=query,
            )
            response = self.client.delete_by_query(
                index=index,
                body={"query": es_query["query"]},
                slices="auto",
                wait_for_completion=True,
                # conflicts="proceed",  # If document version conflict -> continue
            )
            total, deleted = response["total"], response["deleted"]
            return total, deleted

    def search_records(
        self,
        id: str,
        query: BackendRecordsQuery,
        sort: SortConfig,
        record_from: int = 0,
        size: int = 100,
        exclude_fields: List[str] = None,
        enable_highlight: bool = True,
    ) -> Tuple[int, List[Dict[str, Any]]]:

        index = dataset_records_index(id)
        with backend_error_handler(index=index):
            if not sort.sort_by and sort.shuffle is False:
                sort.sort_by = [SortableField(id="id")]  # Default sort by id
            es_query = {
                **self.query_builder.map_2_es_query(
                    schema=self.get_schema(id),
                    query=query,
                    sort=sort,
                ),
                "_source": {"excludes": exclude_fields or []},
                "from": record_from,
            }
            if enable_highlight:
                es_query["highlight"] = self.__configure_query_highlight__()

            results = self._search(index=index, query=es_query, size=size)
            hits = results["hits"]
            total = hits["total"]
            docs = hits["hits"]

            return total, list(map(self.__esdoc2record__, docs))

    def __esdoc2record__(
        self,
        doc: Dict[str, Any],
        is_phrase_query: bool = True,
    ):
        return {
            **doc["_source"],
            "id": doc["_id"],
            "search_keywords": self.__parse_highlight_results__(
                doc, is_phrase_query=is_phrase_query
            ),
        }

    @classmethod
    def __parse_highlight_results__(
        cls,
        doc: Dict[str, Any],
        is_phrase_query: bool = False,
    ) -> Optional[List[str]]:
        highlight_info = doc.get("highlight")
        if not highlight_info:
            return None

        search_keywords = []
        for content in highlight_info.values():
            if not isinstance(content, list):
                content = [content]
            text = " ".join(content)

            if is_phrase_query:
                text = re.sub(cls.__HIGHLIGHT_PHRASE_PRE_PARSER_REGEX__, " ", text)
            search_keywords.extend(re.findall(cls.__HIGHLIGHT_VALUES_REGEX__, text))
        return list(set(search_keywords))

    @classmethod
    def __configure_query_highlight__(cls, task: TaskType = None):

        return {
            "pre_tags": [cls.__HIGHLIGHT_PRE_TAG__],
            "post_tags": [cls.__HIGHLIGHT_POST_TAG__],
            "require_field_match": True,
            "fields": {
                "text": {},
                "text.*": {},
                "inputs.*": {},
                # **({"inputs.*": {}} if task == TaskType.text_classification else {}),
            },
        }

    # TODO(@frascuchon): Include sort parameter
    def scan_records(
        self,
        id: str,
        query: Optional[BackendRecordsQuery] = None,
        id_from: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        index = dataset_records_index(id)
        with backend_error_handler(index):
            es_query = {
                **self.query_builder.map_2_es_query(
                    schema=self.get_schema(id),
                    query=query,
                    id_from=id_from,
                    sort=SortConfig(),  # sort by id as default for proper index scan using search after
                ),
                "highlight": self.__configure_query_highlight__(),
            }
            docs = self._list_documents(index, query=es_query, size=limit)
            for doc in docs:
                yield self.__esdoc2record__(doc)

    def open(self, id: str):
        self.open_index(dataset_records_index(id))

    def get_metadata_mappings(self, id: str):
        records_index = dataset_records_index(id)
        return self._get_field_mapping(index=records_index, field_name="metadata.*")

    def create_dataset_index(
        self,
        id: str,
        task: TaskType,
        metadata_values: Optional[Dict[str, Any]] = None,
        force_recreate: bool = False,
    ) -> None:

        _mappings = tasks_common_mappings()
        task_mappings = self.get_task_mapping(task).copy()
        for k in task_mappings:
            if isinstance(task_mappings[k], list):
                _mappings[k] = [*_mappings.get(k, []), *task_mappings[k]]
            else:
                _mappings[k] = {**_mappings.get(k, {}), **task_mappings[k]}
        index = dataset_records_index(id)
        self._create_index(
            index=index,
            settings=tasks_common_settings(),
            mappings={**tasks_common_mappings(), **_mappings},
            force_recreate=force_recreate,
        )
        if metadata_values:
            self._configure_metadata_fields(id, metadata_values)

    def _configure_metadata_fields(self, id: str, metadata_values: Dict[str, Any]):
        def check_metadata_length(metadata_length: int = 0):
            if metadata_length > settings.metadata_fields_limit:
                raise MetadataLimitExceededError(
                    length=metadata_length,
                    limit=settings.metadata_fields_limit,
                )

        def detect_nested_type(v: Any) -> bool:
            """Returns True if value match as nested value"""
            return isinstance(v, list) and isinstance(v[0], dict)

        index = dataset_records_index(id)
        check_metadata_length(len(metadata_values))
        check_metadata_length(
            len(
                {
                    *self._get_field_mapping(
                        index, "metadata.*", exclude_subfields=True
                    ),
                    *[f"metadata.{k}" for k in metadata_values.keys()],
                }
            )
        )
        for field, value in metadata_values.items():
            if detect_nested_type(value):
                self._create_field_mapping(
                    index,
                    field_name=f"metadata.{field}",
                    mapping=mappings.nested_field(),
                )

    def delete(self, id: str):
        index = dataset_records_index(id)
        try:
            self._delete_index(index, raises_error=True)
        except GenericSearchError as ex:
            if not ex.origin_error.status_code == 400:
                raise ex
            # It's an alias --> DELETE from original index
            original_index = settings.old_dataset_records_index_name.format(id)
            self._delete_index_alias(original_index, alias=index)

        finally:
            self._delete_document(index=DATASETS_INDEX_NAME, doc_id=id)

    def copy(self, id_from: str, id_to: str):
        index_from = dataset_records_index(id_from)
        index_to = dataset_records_index(id_to)

        self._clone_index(index=index_from, clone_to=index_to)

    def close(self, id: str):
        return self._close_index(dataset_records_index(id))

    def create_datasets_index(self, force_recreate: bool = False):
        self._create_index(
            DATASETS_INDEX_NAME,
            force_recreate=force_recreate,
            mappings=datasets_index_mappings(),
        )
        if not settings.enable_migration:
            return

        source_index = settings.old_dataset_index_name
        target_index = DATASETS_INDEX_NAME
        try:
            with backend_error_handler(index=source_index):
                reindex(
                    self.__client__,
                    source_index=source_index,
                    target_index=target_index,
                )
                for doc in scan(self.__client__, index=source_index):
                    dataset_id = doc["_id"]
                    index = settings.old_dataset_records_index_name.format(dataset_id)
                    alias = dataset_records_index(dataset_id)
                    self._create_index_alias(index, alias=alias)
        except IndexNotFoundError:
            pass  # Nothing to migrate

    def list_datasets(self, query: BaseDatasetsQuery):
        with backend_error_handler(index=DATASETS_INDEX_NAME):
            es_query = self.query_builder.map_2_es_query(query=query)
            return self._list_documents(
                index=DATASETS_INDEX_NAME,
                query=es_query,
                fetch_once=True,
                size=self.__MAX_NUMBER_OF_LISTED_DATASETS__,
            )

    def add_dataset_document(self, id: str, document: Dict[str, Any]):
        self._add_document(index=DATASETS_INDEX_NAME, doc_id=id, document=document)

    def update_dataset_document(self, id: str, document: Dict[str, Any]):
        self._update_document(
            index=DATASETS_INDEX_NAME,
            doc_id=id,
            document=document,
            partial_update=True,
        )

    def find_dataset(
        self, id: str, name: Optional[str] = None, owner: Optional[str] = None
    ):
        with backend_error_handler(index=DATASETS_INDEX_NAME):
            document = self._get_document_by_id(index=DATASETS_INDEX_NAME, doc_id=id)
            if not document and owner is None and name:
                # We must search by name since we have no owner
                es_query = self.query_builder.map_2_es_query(
                    query=BaseDatasetsQuery(name=name)
                )
                docs = self._list_documents(
                    index=DATASETS_INDEX_NAME,
                    query=es_query,
                    size=self.__MAX_NUMBER_OF_LISTED_DATASETS__,
                    fetch_once=True,
                )
                docs = list(docs)
                if len(docs) == 0:
                    return None

                if len(docs) > 1:
                    raise ValueError(
                        f"Ambiguous dataset info found for name {name}. Please provide a valid owner"
                    )
                document = docs[0]
            return document

    def compute_argilla_metric(self, metric_id):
        return self._compute_metric(index=DATASETS_INDEX_NAME, metric_id=metric_id)

    def _compute_metric(
        self,
        index: str,
        metric_id: str,
        query: Optional[Any] = None,
        schema: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        metric = self.find_metric_by_id(metric_id)
        # Only for metadata aggregation. In a future could be nice to provide the whole index schema
        params.update(
            {"schema": self._get_field_mapping(index=index, field_name="metadata.*")}
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
                    schema=schema,
                    query=query,
                ),
                "aggs": agg,
            }
            search_result = self._search(index=index, query=es_query, size=0)
            search_aggregations = search_result.get("aggregations", {})

            if search_aggregations:
                parsed_aggregations = query_helpers.parse_aggregations(
                    search_aggregations
                )
                results.update(parsed_aggregations)

        return metric.aggregation_result(results.get(metric_id, results))

    def remove_dataset_field(self, id: str, field: str):
        self._update_document(
            index=DATASETS_INDEX_NAME,
            doc_id=id,
            script=f'ctx._source.remove("{field}")',
            partial_update=True,
        )

    def _extract_index_schema_from_response(
        self, index: str, es_response: Dict[str, Any]
    ):
        if index in es_response:
            return es_response.get(index)
        elif len(es_response) == 1:
            return list(es_response.values())[0]
        return es_response

    def _create_index_alias(self, index: str, alias: str):
        return self.__client__.indices.put_alias(
            index=index,
            name=alias,
            ignore=[400, 404],
        )

    def _delete_index_alias(self, index: str, alias: str):
        self.__client__.indices.delete_alias(index=index, name=alias, ignore=[400, 404])


def dataset_records_index(dataset_id: str) -> str:
    index_mame_template = settings.dataset_records_index_name
    return index_mame_template.format(dataset_id)
