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

import dataclasses
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from opensearchpy import OpenSearch, helpers
from opensearchpy.exceptions import (
    NotFoundError,
    OpenSearchException,
    OpenSearchWarning,
    RequestError,
)
from opensearchpy.helpers import BulkIndexError

from argilla.server.daos.backend import query_helpers
from argilla.server.daos.backend.base import BackendErrorHandler, IndexNotFoundError
from argilla.server.daos.backend.client_adapters.base import IClientAdapter
from argilla.server.daos.backend.metrics.base import ElasticsearchMetric
from argilla.server.daos.backend.search.model import (
    BaseQuery,
    SortableField,
    SortConfig,
)
from argilla.server.daos.backend.search.query_builder import (
    HighlightParser,
    OpenSearchQueryBuilder,
)


@dataclasses.dataclass
class OpenSearchClient(IClientAdapter):
    index_shards: int

    config_backend: Dict[str, Any]
    highlight = HighlightParser()

    query_builder = OpenSearchQueryBuilder()

    def __post_init__(self):
        self.__client__ = OpenSearch(**self.config_backend)
        self.error_handling = BackendErrorHandler(
            WarningIgnore=OpenSearchWarning,
            RequestError=RequestError,
            BulkError=BulkIndexError,
            NotFoundError=NotFoundError,
            GenericApiError=OpenSearchException,
        )

    def configure_index_vectors(
        self,
        *,
        index: str,
        vectors: Dict[str, int],
    ):
        self._check_vector_supported()

        self.set_index_settings(
            index=index,
            settings={"index.knn": False},
        )
        vector_mappings = {}
        for vector_name, vector_dimension in vectors.items():
            index_mapping = {
                "type": "knn_vector",
                "dimension": vector_dimension,
                "method": {
                    "name": "hnsw",
                    "engine": "lucene",
                    "space_type": "l2",
                    "parameters": {"m": 2, "ef_construction": 4},
                },
            }
            vector_field = self.query_builder.get_vector_field_name(vector_name)
            vector_mappings[vector_field] = index_mapping

        self.set_index_mappings(
            index=index,
            properties=vector_mappings,
        )

    def _check_vector_supported(self):
        if not self.vector_search_supported:
            raise ValueError(
                "The vector search is not supported for this elasticsearch version. "
                "Please, update the server to use this feature"
            )

    def search_docs(
        self,
        *,
        index: str,
        query: Optional[BaseQuery] = None,
        sort: Optional[SortConfig] = None,
        doc_from: int = 0,
        size: int = 100,
        exclude_fields: List[str] = None,
        enable_highlight: bool = True,
        routing: str = None,
    ) -> Dict[str, Any]:
        with self.error_handling(index=index):
            highlight = self.highlight if enable_highlight else None
            es_query = self.query_builder.map_2_es_query(
                schema=self.get_index_schema(index=index),
                query=query,
                sort=sort,
                exclude_fields=exclude_fields,
                doc_from=doc_from,
                highlight=highlight,
                size=size,
            )

            results = self._es_search(
                index=index,
                es_query=es_query,
                size=size,
                routing=routing,
            )

            return self._process_search_results(
                search_results=results,
                highlight_parser=highlight,
            )

    def bulk(
        self,
        *,
        index: str,
        actions: Iterable[dict],
    ) -> Tuple:
        with self.error_handling(index=index):
            return helpers.bulk(
                client=self.__client__,
                index=index,
                actions=actions,
                raise_on_error=True,
                refresh="wait_for",
            )

    def _reindex(
        self,
        *,
        source_index: str,
        target_index: str,
    ):
        with self.error_handling(index=source_index):
            helpers.reindex(
                client=self.__client__,
                source_index=source_index,
                target_index=target_index,
            )

    def get_cluster_info(self) -> Dict[str, Any]:
        """Returns basic about es cluster"""
        with self.error_handling():
            return self.__client__.info()

    def get_index_schema(self, *, index: str):
        with self.error_handling(index=index):
            response = self.__client__.indices.get_mapping(index=index)
            if index in response:
                return response.get(index)
            elif len(response) == 1:
                return list(response.values())[0]
            return response

    def drop_document_property(
        self,
        index: str,
        id: str,
        property: str,
    ):
        self.upsert_index_document(
            index=index,
            id=id,
            script=f'ctx._source.remove("{property}")',
            partial_update=True,
        )

    def update_docs_by_query(
        self,
        *,
        index: str,
        data: Dict[str, Any],
        query: Optional[BaseQuery] = None,
    ) -> Dict[str, Any]:
        es_query = self.query_builder.map_2_es_query(
            schema=self.get_index_schema(index=index),
            query=query,
        )
        return self._update_by_query(
            index=index,
            query=es_query["query"],
            data=data,
        )

    def compute_index_metric(
        self,
        *,
        index: str,
        metric: ElasticsearchMetric,
        query: BaseQuery,
        params: Dict[str, Any],
    ):
        params.update(
            {
                "index": index,
                "client": self,
            }
        )

        filtered_params = {argument: params[argument] for argument in metric.metric_arg_names if argument in params}

        aggregations = metric.aggregation_request(**filtered_params)
        if not aggregations:
            return {}
        if not isinstance(aggregations, list):
            aggregations = [aggregations]

        with self.error_handling(index=index):
            es_query = self.query_builder.map_2_es_query(
                schema=self.get_index_schema(index=index),
                query=query,
            )

            results = {}
            for aggregation in aggregations:
                es_query["aggs"] = aggregation

                search = self._es_search(
                    index=index,
                    es_query=es_query,
                    size=0,
                )

                search_aggregations = search.get("aggregations", {})
                if search_aggregations:
                    parsed_aggregations = query_helpers.parse_aggregations(search_aggregations)
                    results.update(parsed_aggregations)
            return metric.aggregation_result(results.get(metric.id, results))

    def delete_docs_by_query(
        self,
        *,
        index: str,
        query: Optional[BaseQuery],
    ) -> Tuple[int, int]:
        es_query = self.query_builder.map_2_es_query(
            schema=self.get_index_schema(index=index),
            query=query,
        )
        return self._delete_by_query(
            index=index,
            query=es_query["query"],
        )

    def _delete_by_query(
        self,
        *,
        index: str,
        query: Dict[str, Any],
    ) -> Tuple[int, int]:
        with self.error_handling(index=index):
            response = self.__client__.delete_by_query(
                index=index,
                body={"query": query},
                slices="auto",
                wait_for_completion=True,
                # conflicts="proceed",  # If document version conflict -> continue
            )
            total, deleted = response["total"], response["deleted"]
            return total, deleted

    def _update_by_query(
        self,
        *,
        index,
        query: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        with self.error_handling(index=index):
            inline = ";".join([f"ctx._source.{k}='{v}'" for k, v in data.items()])
            response = self.__client__.update_by_query(
                index=index,
                body={
                    "query": query,
                    "script": {
                        "lang": "painless",
                        "inline": inline,
                    },
                },
                slices="auto",
                wait_for_completion=True,
                conflicts="proceed",
            )
            return {
                "total": response["total"],
                "updated": response["updated"],
            }

    def scan_docs(
        self,
        index: str,
        query: BaseQuery,
        sort: SortConfig,
        size: Optional[int] = None,
        fetch_once: bool = False,
        search_from_params: Optional[Any] = None,
        enable_highlight: bool = False,
        include_fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
    ) -> Iterable[Dict[str, Any]]:
        batch_size = size or 500

        highlight = self.highlight if enable_highlight else None
        es_query = self.query_builder.map_2_es_query(
            query=query,
            schema=self.get_index_schema(index=index),
            sort=sort,
            search_after_param=search_from_params,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            highlight=highlight,
        )
        es_query = es_query.copy() or {}
        response = self.__client__.search(
            index=index,
            body=es_query,
            size=batch_size,
            track_total_hits=False,
        )
        records_yield = 0
        while response["hits"]["hits"]:
            hit = None
            for hit in response["hits"]["hits"]:
                yield self._normalize_document(document=hit, highlight=highlight, add_sort_info=True)
                records_yield += 1

            if fetch_once or (size and size >= records_yield):
                break

            next_search_from = hit["sort"]
            es_query["search_after"] = next_search_from
            response = self.__client__.search(index=index, body=es_query, size=size, track_total_hits=False)

    def _process_search_results(
        self,
        *,
        search_results: Dict[str, Any],
        highlight_parser: Optional[HighlightParser] = None,
    ):
        hits = search_results["hits"]
        total = hits["total"]
        docs = hits["hits"]
        return {
            "total": total,
            "docs": [
                self._normalize_document(
                    document=doc,
                    highlight=highlight_parser,
                )
                for doc in docs
            ],
        }

    def copy_index(
        self,
        *,
        source_index: str,
        target_index: str,
        override: bool = True,
        reindex: bool = False,
    ):
        source_index = self._get_original_index_name(source_index)

        if reindex:
            return self._reindex(source_index=source_index, target_index=target_index)

        is_source_read_only_index = self._is_read_only_index(index=source_index)

        try:
            if not is_source_read_only_index:
                self._enable_or_disable_read_only_index(index=source_index, read_only=True)

            if override:
                self.delete_index(index=target_index)

            self._clone_index(index_from=source_index, index_to=target_index)
        finally:
            self._enable_or_disable_read_only_index(index=source_index, read_only=is_source_read_only_index)
            self._enable_or_disable_read_only_index(index=target_index, read_only=is_source_read_only_index)

    def _clone_index(
        self,
        *,
        index_from: str,
        index_to: str,
    ):
        with self.error_handling(index=index_from):
            self.__client__.indices.clone(
                index=index_from,
                target=index_to,
                wait_for_active_shards=self.index_shards,
            )

    def get_property_type(
        self,
        *,
        index: str,
        property_name: str,
        drop_extra_props: bool = False,
    ) -> Dict[str, str]:
        try:
            schema = self._get_fields_schema(
                index=index,
                fields=f"{property_name}.*",
            )

            if drop_extra_props:
                # Remove `text`, `exact` and `wordcloud` fields
                def is_subfield(key: str):
                    for suffix in ["exact", "text", "wordcloud"]:
                        if suffix in key:
                            return True
                    return False

                schema = {key: value for key, value in schema.items() if not is_subfield(key)}

            return schema
        except IndexNotFoundError:
            # No mapping data
            return {}

    def get_index_document_by_id(
        self,
        index: str,
        id: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            with self.error_handling(index=index):
                if self.__client__.exists(
                    index=index,
                    id=id,
                ):
                    doc = self.__client__.get(index=index, id=id)
                    return self._normalize_document(document=doc)
        # TODO: Review this exception when not found an document instead of an index
        except IndexNotFoundError:
            return None

    def create_index_alias(
        self,
        *,
        index: str,
        alias: str,
    ):
        with self.error_handling(index=index):
            self.__client__.indices.put_alias(
                index=index,
                name=alias,
                ignore=[400, 404],
            )

    def delete_index_document(
        self,
        index: str,
        id: str,
    ):
        with self.error_handling(index=index):
            if self.__client__.exists(
                index=index,
                id=id,
            ):
                self.__client__.delete(
                    index=index,
                    id=id,
                    refresh=True,
                )

    def delete_index_alias(
        self,
        *,
        index: str,
        alias: str,
    ):
        with self.error_handling(index=index):
            self.__client__.indices.delete_alias(
                index=index,
                name=alias,
                ignore=[400, 404],
            )

    def exists_index(self, index: str) -> bool:
        with self.error_handling(index=index):
            return self.__client__.indices.exists(index=index)

    def delete_index(
        self,
        *,
        index: str,
        raises_error: bool = False,
    ):
        with self.error_handling(index=index):
            if self.exists_index(index):
                ignore_errors = [400, 404]
                if raises_error:
                    ignore_errors.clear()
                self.__client__.indices.delete(
                    index=index,
                    ignore=ignore_errors,
                )

    def create_index(
        self,
        index: str,
        force_recreate: bool = False,
        settings: Dict[str, Any] = None,
        mappings: Dict[str, Any] = None,
    ):
        with self.error_handling(index):
            if force_recreate:
                self.delete_index(index=index)
            if not self.exists_index(index=index):
                self.__client__.indices.create(
                    index=index,
                    body={
                        "settings": settings or {},
                        "mappings": mappings or {},
                    },
                    ignore=400,
                )

    def index_documents(self, index: str, docs: List[Dict[str, Any]]) -> int:
        actions = (self._doc2bulk_action(index, doc) for doc in docs)
        success, failed = self.bulk(
            index=index,
            actions=actions,
        )
        return len(failed)

    @staticmethod
    def _doc2bulk_action(index: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        doc_id = doc.get("id")

        data = (
            {"_index": index, "_op_type": "index", **doc}
            if doc_id is None
            else {"_index": index, "_id": doc_id, "_op_type": "update", "doc_as_upsert": True, "doc": doc}
        )

        return data

    def upsert_index_document(
        self,
        index: str,
        id: str,
        document: Optional[Dict[str, Any]] = None,
        script: Optional[str] = None,
        partial_update: bool = False,
    ):
        # TODO: validate either doc or script are provided
        with self.error_handling(index=index):
            if not partial_update:
                return self.index_document(
                    index=index,
                    id=id,
                    body=document,
                )

            return self.update_document(
                index=index,
                id=id,
                body={"script": script} if script else {"doc": document},
            )

    def index_document(
        self,
        *,
        index: str,
        id: str,
        body: dict,
    ):
        with self.error_handling(index=index):
            return self.__client__.index(
                index=index,
                id=id,
                body=body,
                refresh=True,
            )

    def update_document(
        self,
        *,
        index: str,
        id: str,
        body: dict,
    ):
        with self.error_handling(index=index):
            return self.__client__.update(
                index=index,
                id=id,
                body=body,
                refresh=True,
                retry_on_conflict=500,  # TODO: configurable
            )

    def open_index(self, index: str):
        with self.error_handling(index=index):
            self.__client__.indices.open(
                index=index,
                wait_for_active_shards=self.index_shards,
            )

    def close_index(self, index: str):
        with self.error_handling(index=index):
            self.__client__.indices.close(
                index=index,
                ignore_unavailable=True,
                wait_for_active_shards=self.index_shards,
            )

    def clone_index(
        self,
        source_index: str,
        target_index: str,
    ):
        with self.error_handling(index=source_index):
            self.__client__.indices.clone(
                index=source_index,
                target=target_index,
                wait_for_active_shards=self.index_shards,
            )

    def _is_read_only_index(self, index: str) -> bool:
        with self.error_handling(index=index):
            response = self.__client__.indices.get_settings(
                index=index,
                name="index.blocks.write",
                allow_no_indices=True,
                flat_settings=True,
            )
            if not response:
                return False

            return response[index]["settings"]["index.blocks.write"] == "true"

    def set_index_settings(
        self,
        index: str,
        settings: Dict[str, Any],
    ):
        with self.error_handling(index=index):
            try:
                self.close_index(index)
                self.__client__.indices.put_settings(
                    index=index,
                    body=settings,
                )
            finally:
                self.open_index(index)

    def set_index_mappings(
        self,
        index: str,
        properties: Optional[Dict[str, Any]] = None,
        **extra_cfg,
    ):
        with self.error_handling(index=index):
            body = extra_cfg or {}
            if properties:
                body.update({"properties": properties})

            self.__client__.indices.put_mapping(
                index=index,
                body=body,
            )

    def _enable_or_disable_read_only_index(
        self,
        *,
        index: str,
        read_only: bool,
    ):
        with self.error_handling(index=index):
            self.__client__.indices.put_settings(
                index=index,
                body={"settings": {"index.blocks.write": read_only}},
                ignore=404,
            )

    def _get_fields_schema(
        self,
        *,
        index: str,
        fields: str,
    ):
        with self.error_handling(index=index):
            response = self.__client__.indices.get_field_mapping(
                fields=fields,
                index=index,
                ignore_unavailable=False,
            )
            if index in response:
                data = response.get(index)
            elif len(response) == 1:
                data = list(response.values())[0]
            else:
                data = response

            return {
                key: list(definition["mapping"].values())[0]["type"] for key, definition in data["mappings"].items()
            }

    def _normalize_document(
        self,
        document: Dict[str, Any],
        highlight: Optional[HighlightParser] = None,
        is_phrase_query: bool = True,
        add_sort_info: bool = False,
    ):
        data = {
            **document["_source"],
            "id": document["_id"],
        }

        if add_sort_info and "sort" in document:
            data["sort"] = document["sort"]

        if highlight:
            keywords = highlight.parse_highligth_results(
                doc=document,
                is_phrase_query=is_phrase_query,
            )
            if keywords:
                data[highlight.search_keywords_field] = keywords

        return data

    def _es_search(
        self,
        index: str,
        es_query: Dict[str, Any],
        size: int,
        routing: Optional[str] = None,
    ):
        if "knn" in es_query["query"]:
            self._check_vector_supported()

        results = self.__client__.search(
            index=index,
            body=es_query,
            routing=routing,
            track_total_hits=True,
            rest_total_hits_as_int=True,
            size=size,
        )
        return results

    def _get_original_index_name(self, source_index_or_alias: str):
        response = self.__client__.indices.get(index=source_index_or_alias)
        # The response contains a single key with the original index name (if we provided an alias)
        for index_name in response:
            return index_name
