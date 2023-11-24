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

import pytest
from argilla.server.search_engine import ElasticSearchEngine
from argilla.server.search_engine.commons import ALL_RESPONSES_STATUSES_FIELD, es_index_name_for_dataset
from argilla.server.settings import settings
from opensearchpy import OpenSearch
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def test_create_index_with_existing_index(self, search_engine: ElasticSearchEngine, opensearch: OpenSearch):
        from elasticsearch8 import RequestError

        dataset = await DatasetFactory.create()

        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        with pytest.raises(RequestError, match="resource_already_exists_exception"):
            await search_engine.create_index(dataset)
