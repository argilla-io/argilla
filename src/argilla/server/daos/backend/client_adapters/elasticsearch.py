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
from typing import Any, Dict, Iterable, List, Optional, Tuple

from elasticsearch import (
    ApiError,
    Elasticsearch,
    ElasticsearchWarning,
    NotFoundError,
    RequestError,
    helpers,
)
from overrides import overrides

from argilla.server.daos.backend.base import BackendErrorHandler
from argilla.server.daos.backend.client_adapters.opensearch import OpenSearchClient
from argilla.server.daos.backend.search.model import BaseQuery, SortConfig
from argilla.server.daos.backend.search.query_builder import EsQueryBuilder


@dataclasses.dataclass
class ElasticsearchClient(OpenSearchClient):
    query_builder = EsQueryBuilder()

    def __post_init__(self):
        self.__client__ = Elasticsearch(**self.config_backend)
        self.error_handling = BackendErrorHandler(
            WarningIgnore=ElasticsearchWarning,
            RequestError=RequestError,
            NotFoundError=NotFoundError,
            GenericApiError=ApiError,
        )

    @overrides
    def configure_index_vectors(
        self,
        *,
        index: str,
        vectors: Dict[str, int],
        similarity_metric: str = "l2_norm",
    ):
        self._check_vector_supported()

        embedding_mappings = {}
        for embedding_name, embedding_dimension in vectors.items():
            index_mapping = {
                "type": "dense_vector",
                "dims": embedding_dimension,
                "index": True,
                # can similarity property also be part of config @frascuchon ?
                # relates vector search similarity metric
                "similarity": similarity_metric,  ## default value regarding the knn best practices es documentation
            }
            embedding_mappings[embedding_name] = index_mapping

        self.set_index_mappings(
            index=index,
            mappings=embedding_mappings,
        )

    def reindex(
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

    @overrides
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

    @overrides
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

            knn = es_query.pop("knn", None)
            if knn:
                self._check_vector_supported()
                source = es_query["_source"]
                results = self.__client__.search(
                    index=index,
                    knn=knn,
                    routing=routing,
                    source=source,
                    track_total_hits=True,
                    rest_total_hits_as_int=True,
                    size=size,
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

            return self._process_search_results(
                search_results=results,
                highlight_parser=highlight,
            )
