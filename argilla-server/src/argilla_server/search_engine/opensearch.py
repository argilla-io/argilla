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
from typing import Any, Dict, List, Optional
from uuid import UUID

from opensearchpy import AsyncOpenSearch, helpers

from argilla_server.constants import SEARCH_ENGINE_OPENSEARCH
from argilla_server.models import VectorSettings
from argilla_server.search_engine.base import SearchEngine
from argilla_server.search_engine.commons import (
    BaseElasticAndOpenSearchEngine,
    es_bool_query,
    es_field_for_vector_settings,
    es_ids_query,
)
from argilla_server.settings import settings


@SearchEngine.register(engine_name=SEARCH_ENGINE_OPENSEARCH)
@dataclasses.dataclass
class OpenSearchEngine(BaseElasticAndOpenSearchEngine):
    config: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.client = AsyncOpenSearch(**self.config)

    @classmethod
    async def new_instance(cls) -> "OpenSearchEngine":
        config = dict(
            hosts=settings.elasticsearch,
            verify_certs=settings.elasticsearch_ssl_verify,
            ca_certs=settings.elasticsearch_ca_path,
            retry_on_timeout=True,
            max_retries=5,
        )
        return cls(
            config=config,
            number_of_shards=settings.es_records_index_shards,
            number_of_replicas=settings.es_records_index_replicas,
            default_total_fields_limit=settings.es_mapping_total_fields_limit,
        )

    async def close(self):
        await self.client.close()

    async def ping(self) -> bool:
        return await self.client.ping()

    async def info(self) -> dict:
        return await self.client.info()

    def _configure_index_settings(self):
        base_settings = super()._configure_index_settings()
        return {**base_settings, "index.knn": False}

    def _mapping_for_vector_settings(self, vector_settings: VectorSettings) -> dict:
        return {
            es_field_for_vector_settings(vector_settings): {
                "type": "knn_vector",
                "dimension": vector_settings.dimensions,
                "method": {
                    "name": "hnsw",
                    "engine": "lucene",  # See https://opensearch.org/blog/Expanding-k-NN-with-Lucene-aNN/
                    "space_type": "cosinesimil",
                    "parameters": {"m": 2, "ef_construction": 4},
                },
            }
        }

    async def _request_similarity_search(
        self,
        index: str,
        vector_settings: VectorSettings,
        value: List[float],
        k: int,
        excluded_id: Optional[UUID] = None,
        query_filters: Optional[List[dict]] = None,
    ) -> dict:
        knn_query = {"vector": value, "k": k}

        if excluded_id:
            # See https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn/#efficient-k-nn-filtering
            # Will work from Opensearch >= v2.4.0
            knn_query["filter"] = es_bool_query(must_not=[es_ids_query([str(excluded_id)])])

        body = {"query": {"knn": {es_field_for_vector_settings(vector_settings): knn_query}}}

        if query_filters:
            # IMPORTANT: Including boolean filters as part knn filter may return query errors if responses are not
            # created for requested user (with exists query clauses). This is not happening with Elasticsearch.
            # The only way make it work is to use them as a post_filter.
            # See this issue for more details https://github.com/opensearch-project/k-NN/issues/1286
            body["post_filter"] = es_bool_query(should=query_filters, minimum_should_match=len(query_filters))

        return await self.client.search(index=index, body=body, _source=False, track_total_hits=True, size=k)

    async def _create_index_request(self, index_name: str, mappings: dict, settings: dict) -> None:
        await self.client.indices.create(index=index_name, body=dict(settings=settings, mappings=mappings))

    async def _delete_index_request(self, index_name: str):
        await self.client.indices.delete(index_name, ignore=[404], ignore_unavailable=True)

    async def _update_document_request(self, index_name: str, id: str, body: dict):
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-refresh.html#refresh-api-desc
        await self.client.update(index=index_name, id=id, body=body, refresh=True)

    async def put_index_mapping_request(self, index: str, mappings: dict):
        await self.client.indices.put_mapping(index=index, body={"properties": mappings})

    async def _index_search_request(
        self,
        index: str,
        query: dict,
        size: Optional[int] = None,
        from_: Optional[int] = None,
        sort: Optional[dict] = None,
        aggregations: Optional[dict] = None,
    ) -> dict:
        body = {"query": query}
        if aggregations:
            body["aggs"] = aggregations

        if sort:
            body["sort"] = sort

        return await self.client.search(
            index=index,
            body=body,
            from_=from_,
            size=size,
            _source=False,
            track_total_hits=True,
        )

    async def _index_exists_request(self, index_name: str) -> bool:
        return await self.client.indices.exists(index=index_name)

    async def _bulk_op_request(self, actions: List[Dict[str, Any]]):
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-refresh.html#refresh-api-desc
        _, errors = await helpers.async_bulk(client=self.client, actions=actions, raise_on_error=False, refresh=True)
        if errors:
            raise RuntimeError(errors)

    async def _refresh_index_request(self, index_name: str):
        await self.client.indices.refresh(index=index_name)
