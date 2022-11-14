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

from opensearchpy import NotFoundError, OpenSearch, RequestError, helpers
from opensearchpy.exceptions import OpenSearchException, OpenSearchWarning
from overrides import overrides

from argilla.server.daos.backend.base import BackendErrorHandler
from argilla.server.daos.backend.client_adapters.elasticsearch import (
    ElasticsearchClient,
)
from argilla.server.daos.backend.search.model import BaseQuery, SortConfig
from argilla.server.daos.backend.search.query_builder import OpenSearchQueryBuilder


@dataclasses.dataclass
class OpenSearchClient(ElasticsearchClient):

    query_builder = OpenSearchQueryBuilder()

    @overrides
    def __post_init__(self):
        self.__client__ = OpenSearch(**self.config_backend)
        self.error_handling = BackendErrorHandler(
            WarningIgnore=OpenSearchWarning,
            RequestError=RequestError,
            NotFoundError=NotFoundError,
            GenericApiError=OpenSearchException,
        )

    @overrides
    def configure_index_vectors(
        self,
        *,
        index: str,
        vectors: Dict[str, int],
    ):
        if not self.vector_search_supported:
            raise ValueError(
                "The vector search is not supported for this elasticsearch version. "
                "Please, update the server to use this feature"
            )

        self.set_index_settings(
            index=index,
            settings={
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100,
                }
            },
        )
        embedding_mappings = {}
        for embedding_name, embedding_dimension in vectors.items():
            index_mapping = {
                "type": "knn_vector",
                "dimension": embedding_dimension,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 128,
                        "m": 24,
                    },
                },
            }
            embedding_mappings[embedding_name] = index_mapping

        self.set_index_mappings(
            index=index,
            mappings=embedding_mappings,
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
            )

            if "knn" in es_query["query"] and not self.vector_search_supported:
                raise ValueError(
                    "The vector search is not supported for this elasticsearch version. "
                    "Please, update the elasticsearch server to use this feature"
                )

            results = self.__client__.search(
                index=index,
                body=es_query,
                routing=routing,
                track_total_hits=True,
                rest_total_hits_as_int=True,
                size=size,
            )

            return self._process_search_results(
                search_results=results,
                highlight_parser=highlight,
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
