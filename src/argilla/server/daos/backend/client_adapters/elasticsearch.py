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
from typing import Any, Dict, Iterable, Optional, Tuple

import elasticsearch
from elasticsearch import Elasticsearch, NotFoundError, RequestError, helpers
from elasticsearch.helpers import BulkIndexError
from packaging.version import parse

from argilla.server.daos.backend.base import BackendErrorHandler
from argilla.server.daos.backend.client_adapters.opensearch import OpenSearchClient
from argilla.server.daos.backend.search.query_builder import EsQueryBuilder

ES_CLIENT_VERSION: str = elasticsearch.__versionstr__

if parse(elasticsearch.__versionstr__) >= parse("8.0"):
    from elasticsearch import ApiError, ElasticsearchWarning
else:
    from elasticsearch.exceptions import ElasticsearchException as ApiError
    from elasticsearch.exceptions import ElasticsearchWarning


@dataclasses.dataclass
class ElasticsearchClient(OpenSearchClient):
    ES_CLIENT_VERSION = ES_CLIENT_VERSION
    query_builder = EsQueryBuilder()

    def __post_init__(self):
        self.__client__ = Elasticsearch(**self.config_backend)
        self.error_handling = BackendErrorHandler(
            WarningIgnore=ElasticsearchWarning,
            RequestError=RequestError,
            BulkError=BulkIndexError,
            NotFoundError=NotFoundError,
            GenericApiError=ApiError,
        )

    def configure_index_vectors(
        self,
        *,
        index: str,
        vectors: Dict[str, int],
        similarity_metric: str = "l2_norm",
    ):
        self._check_vector_supported()

        vector_mappings = {}
        for vector_name, vector_dimension in vectors.items():
            index_mapping = {
                "type": "dense_vector",
                "dims": vector_dimension,
                "index": True,
                # can similarity property also be part of config @frascuchon ?
                # relates vector search similarity metric
                "similarity": similarity_metric,  ## default value regarding the knn best practices es documentation
            }
            vector_field = self.query_builder.get_vector_field_name(vector_name)
            vector_mappings[vector_field] = index_mapping

        self.set_index_mappings(
            index=index,
            properties=vector_mappings,
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

    def _es_search(
        self,
        index: str,
        es_query: Dict[str, Any],
        size: int,
        routing: Optional[str] = None,
    ):
        knn = es_query.pop("knn", None)
        if knn:
            self._check_vector_supported()
            results = self.__client__.search(
                index=index,
                knn=knn,
                query=es_query.get("query"),
                aggs=es_query.get("aggs"),
                routing=routing,
                track_total_hits=True,
                rest_total_hits_as_int=True,
                size=size,
                source=es_query.get("_source"),
            )
        else:
            results = self.__client__.search(
                index=index,
                routing=routing,
                body=es_query,
                track_total_hits=True,
                rest_total_hits_as_int=True,
                size=size,
            )
        return results
