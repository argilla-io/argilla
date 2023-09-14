import dataclasses
from typing import Any, AsyncGenerator, Dict, List, Optional

from elasticsearch8 import AsyncElasticsearch, helpers
from pydantic import conint

from argilla.server.models import Dataset, Record, VectorSettings
from argilla.server.search_engine import (
    SearchEngine,
    SearchResponses,
    UserResponseStatusFilter,
)
from argilla.server.search_engine.commons import BaseElasticAndOpenSearchEngine, field_name_for_vector_settings
from argilla.server.settings import settings


def _compute_num_candidates_from_k(k: int):
    if k < 50:
        return 500
    elif 50 <= k < 200:
        return 100
    return 2000


@dataclasses.dataclass
class ElasticSearchEngine(BaseElasticAndOpenSearchEngine):
    config: Dict[str, Any]

    es_number_of_shards: int
    es_number_of_replicas: int

    def __post_init__(self):
        self.client = AsyncElasticsearch(**self.config)

    async def similarity_search(
        self,
        dataset: Dataset,
        vector_settings: VectorSettings,
        value: Optional[List[float]] = None,
        record: Optional[Record] = None,
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        max_results: conint(ge=2, le=500) = 100,
        threshold: Optional[float] = None,
    ) -> SearchResponses:
        if not (value or record):
            raise ValueError("Must provide vector value or record to compute the similarity search")

        vector_value = value
        if not vector_value:
            vector_value = record.vector_by_vector_settings_id(vector_settings.id).value

        index = await self._get_index_or_raise(dataset)
        response = await self._request_similarity_search(
            index=index,
            vector_settings=vector_settings,
            value=vector_value,
            k=max_results,
            user_response_status_filter=user_response_status_filter,
        )

        return await self._process_search_response(response, threshold)

    def _configure_index_settings(self):
        return {
            "number_of_shards": self.es_number_of_shards,
            "number_of_replicas": self.es_number_of_replicas,
        }

    def _mapping_for_vector_settings(self, vector_settings: VectorSettings) -> dict:
        return {
            f"vectors.{vector_settings.id}": {
                "type": "dense_vector",
                "dims": vector_settings.dimensions,
                "index": True,
                # can similarity property also be part of config @frascuchon ?
                # relates vector search similarity metric
                "similarity": "l2_norm",  ## default value regarding the knn best practices es documentation
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
        knn_query = {
            "field": field_name_for_vector_settings(vector_settings),
            "query_vector": value,
            "k": k,
            "num_candidates": _compute_num_candidates_from_k(k=k),
        }

        if user_response_status_filter:
            knn_query["filter"] = self._response_status_filter_builder(user_response_status_filter)

        return await self.client.search(index=index, knn=knn_query, _source=False, track_total_hits=True)

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

    async def _create_index_request(self, index_name: str, mappings: dict, settings: dict) -> None:
        await self.client.indices.create(index=index_name, settings=settings, mappings=mappings)

    async def _delete_index_request(self, index_name: str):
        await self.client.indices.delete(index_name, ignore=[404], ignore_unavailable=True)

    async def _update_document_request(self, index_name: str, id: str, body: dict):
        await self.client.update(index=index_name, id=id, **body)

    async def put_index_mapping_request(self, index: str, mappings: dict):
        await self.client.indices.put_mapping(index=index, properties=mappings)

    async def _index_search_request(self, index: str, query: dict, size: int, from_: int):
        return await self.client.search(
            index=index,
            query=query,
            from_=from_,
            size=size,
            source=False,
            sort="_score:desc,id:asc",
            track_total_hits=True,
        )

    async def _index_exists_request(self, index_name: str) -> bool:
        return await self.client.indices.exists(index=index_name)

    async def _bulk_op_request(self, actions: List[Dict[str, Any]]):
        _, errors = await helpers.async_bulk(client=self.client, actions=actions, raise_on_error=False)
        if errors:
            raise RuntimeError(errors)


async def get_search_engine() -> AsyncGenerator[SearchEngine, None]:
    config = dict(
        hosts=settings.elasticsearch,
        verify_certs=settings.elasticsearch_ssl_verify,
        ca_certs=settings.elasticsearch_ca_path,
        retry_on_timeout=True,
        max_retries=5,
    )
    search_engine = ElasticSearchEngine(
        config,
        es_number_of_shards=settings.es_records_index_shards,
        es_number_of_replicas=settings.es_records_index_replicas,
    )
    try:
        yield search_engine
    finally:
        await search_engine.client.close()
