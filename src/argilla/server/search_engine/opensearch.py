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

from opensearchpy import AsyncOpenSearch, helpers

from argilla.server.models import (
    VectorSettings,
)
from argilla.server.search_engine.base import (
    SearchEngine,
    UserResponseStatusFilter,
)
from argilla.server.search_engine.commons import BaseElasticAndOpenSearchEngine, field_name_for_vector_settings
from argilla.server.settings import settings


@SearchEngine.register(engine_name="opensearch")
@dataclasses.dataclass
class OpenSearchEngine(BaseElasticAndOpenSearchEngine):
    config: Dict[str, Any]

    es_number_of_shards: int
    es_number_of_replicas: int

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
            config,
            es_number_of_shards=settings.es_records_index_shards,
            es_number_of_replicas=settings.es_records_index_replicas,
        )

    async def close(self):
        await self.client.close()

    def _configure_index_mappings(self, dataset) -> dict:
        return {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "dynamic_templates": self._dynamic_templates_for_question_responses(dataset.questions),
            "properties": {
                # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
                "id": {"type": "keyword"},
                "responses": {"dynamic": True, "type": "object"},
                **self._mapping_for_vectors_settings(dataset.vectors_settings),
                **self._mapping_for_fields(dataset.fields),
            },
        }

    def _configure_index_settings(self):
        return {
            "index.knn": False,
            "number_of_shards": self.es_number_of_shards,
            "number_of_replicas": self.es_number_of_replicas,
        }

    def _mapping_for_vector_settings(self, vector_settings: VectorSettings) -> dict:
        return {
            field_name_for_vector_settings(vector_settings): {
                "type": "knn_vector",
                "dimension": vector_settings.dimensions,
                "method": {
                    "name": "hnsw",
                    "engine": "lucene",  # See https://opensearch.org/blog/Expanding-k-NN-with-Lucene-aNN/
                    "space_type": "l2",
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
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
    ) -> dict:
        knn_query = {field_name_for_vector_settings(vector_settings): {"vector": value, "k": k}}

        if user_response_status_filter:
            # See https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn/#efficient-k-nn-filtering
            # Will work from Opensearch >= v2.4
            knn_query["filter"] = self._response_status_filter_builder(user_response_status_filter)

        body = {"query": {"knn": knn_query}}
        return await self.client.search(index=index, body=body, _source=False, track_total_hits=True)

    async def _create_index_request(self, index_name: str, mappings: dict, settings: dict) -> None:
        await self.client.indices.create(index=index_name, body=dict(settings=settings, mappings=mappings))

    async def _delete_index_request(self, index_name: str):
        await self.client.indices.delete(index_name, ignore=[404], ignore_unavailable=True)

    async def _update_document_request(self, index_name: str, id: str, body: dict):
        await self.client.update(index=index_name, id=id, body=body)

    async def put_index_mapping_request(self, index: str, mappings: dict):
        await self.client.indices.put_mapping(index=index, body={"properties": mappings})

    async def _index_search_request(self, index: str, query: dict, size: int, from_: int):
        return await self.client.search(
            index=index,
            body={"query": query},
            from_=from_,
            size=size,
            _source=False,
            sort="_score:desc,id:asc",
            track_total_hits=True,
        )

    async def _index_exists_request(self, index_name: str) -> bool:
        return await self.client.indices.exists(index=index_name)

    async def _bulk_op_request(self, actions: List[Dict[str, Any]]):
        _, errors = await helpers.async_bulk(client=self.client, actions=actions, raise_on_error=False)
        if errors:
            raise RuntimeError(errors)
