import pytest
from opensearchpy import OpenSearch
from sqlalchemy.ext.asyncio import AsyncSession

from argilla.server.search_engine import ElasticSearchEngine
from argilla.server.search_engine.commons import ALL_RESPONSES_STATUSES_FIELD, es_index_name_for_dataset
from argilla.server.settings import settings
from tests.factories import DatasetFactory, VectorSettingsFactory
from tests.unit.server.search_engine.test_commons import refresh_dataset


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.search_engine == "elasticsearch", reason="Running on elasticsearch engine")
class TestElasticSearchEngine:

    async def test_create_index_for_dataset(
        self, elasticsearch_engine: ElasticSearchEngine, db: AsyncSession, opensearch: OpenSearch
    ):
        dataset = await DatasetFactory.create()

        await refresh_dataset(dataset)
        await elasticsearch_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [
                {
                    "status_responses": {
                        "mapping": {"type": "keyword", "copy_to": ALL_RESPONSES_STATUSES_FIELD},
                        "path_match": "responses.*.status",
                    }
                }
            ],
            "properties": {
                "id": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                ALL_RESPONSES_STATUSES_FIELD: {"type": "keyword"},
                "responses": {"dynamic": "true", "type": "object"},
                "metadata": {"dynamic": "false", "type": "object"},
            },
        }

        assert index["settings"]["index"]["number_of_shards"] == str(elasticsearch_engine.number_of_shards)
        assert index["settings"]["index"]["number_of_replicas"] == str(elasticsearch_engine.number_of_replicas)

    async def test_create_dataset_index_with_vectors(self, search_engine: ElasticSearchEngine, opensearch: OpenSearch):
        vectors_settings = await VectorSettingsFactory.create_batch(5)
        dataset = await DatasetFactory.create(vectors_settings=vectors_settings)

        await refresh_dataset(dataset)
        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["vectors"]["properties"] == {
            str(settings.id): {
                "type": "dense_vector",
                "dims": settings.dimensions,
                "index": True,
                "similarity": "cosine",
            }
            for settings in vectors_settings
        }