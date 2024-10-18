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

from elasticsearch8 import AsyncElasticsearch, helpers

from argilla_server.constants import SEARCH_ENGINE_ELASTICSEARCH
from argilla_server.models import VectorSettings
from argilla_server.search_engine import SearchEngine
from argilla_server.search_engine.commons import (
    BaseElasticAndOpenSearchEngine,
    es_bool_query,
    es_field_for_vector_settings,
    es_ids_query,
)
from argilla_server.settings import settings


def _compute_num_candidates_from_k(k: int) -> int:
    if k < 50:
        return 500
    elif 50 <= k < 200:
        return 100
    return 2000


@SearchEngine.register(engine_name=SEARCH_ENGINE_ELASTICSEARCH)
@dataclasses.dataclass
class ElasticSearchEngine(BaseElasticAndOpenSearchEngine):
    config: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.client = AsyncElasticsearch(**self.config)

    @classmethod
    async def new_instance(cls) -> "ElasticSearchEngine":
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

    def _mapping_for_vector_settings(self, vector_settings: VectorSettings) -> dict:
        return {
            es_field_for_vector_settings(vector_settings): {
                "type": "dense_vector",
                "dims": vector_settings.dimensions,
                "index": True,
                # can similarity property also be part of config @frascuchon ?
                # relates vector search similarity metric
                # "similarity": "l2_norm",  ## default value regarding the knn best practices es documentation
                "similarity": "cosine",
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
        knn_query = {
            "field": es_field_for_vector_settings(vector_settings),
            "query_vector": value,
            "k": k,
            "num_candidates": _compute_num_candidates_from_k(k=k),
        }

        if bool(excluded_id) or bool(query_filters):
            minimum_should_match = None
            must_not_filters = None

            if excluded_id:
                must_not_filters = [es_ids_query([str(excluded_id)])]
            if query_filters:
                minimum_should_match = len(query_filters)

            bool_filter_query = es_bool_query(
                should=query_filters, minimum_should_match=minimum_should_match, must_not=must_not_filters
            )

            knn_query["filter"] = bool_filter_query
        return await self.client.search(index=index, knn=knn_query, _source=False, track_total_hits=True, size=k)

    async def _create_index_request(self, index_name: str, mappings: dict, settings: dict) -> None:
        await self.client.indices.create(index=index_name, settings=settings, mappings=mappings)

    async def _delete_index_request(self, index_name: str):
        await self.client.indices.delete(index=index_name, ignore=[404], ignore_unavailable=True)

    async def _update_document_request(self, index_name: str, id: str, body: dict):
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-refresh.html
        await self.client.update(index=index_name, id=id, **body, refresh="wait_for")

    async def put_index_mapping_request(self, index: str, mappings: dict):
        await self.client.indices.put_mapping(index=index, properties=mappings)

    async def _index_search_request(
        self,
        index: str,
        query: dict,
        size: Optional[int] = None,
        from_: Optional[int] = None,
        sort: Optional[dict] = None,
        aggregations: Optional[dict] = None,
    ) -> dict:
        return await self.client.search(
            index=index,
            query=query,
            from_=from_,
            size=size,
            source=False,
            aggregations=aggregations,
            sort=sort,
            track_total_hits=True,
        )

    async def _index_exists_request(self, index_name: str) -> bool:
        return await self.client.indices.exists(index=index_name)

    async def _bulk_op_request(self, actions: List[Dict[str, Any]]):
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-refresh.html
        _, errors = await helpers.async_bulk(
            client=self.client,
            actions=actions,
            raise_on_error=False,
            refresh="wait_for",
        )

        for error in errors:
            self._LOGGER.error(f"Error in bulk operation: {error}")
