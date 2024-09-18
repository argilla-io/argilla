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
from argilla_server.search_engine import OpenSearchEngine
from argilla_server.search_engine.commons import es_index_name_for_dataset
from argilla_server.settings import settings
from opensearchpy import OpenSearch, RequestError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import DatasetFactory, VectorSettingsFactory
from tests.unit.search_engine.test_commons import refresh_dataset


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.search_engine == "opensearch", reason="Running on opensearch engine")
class TestOpenSearchEngine:
    async def test_create_index_for_dataset(
        self, opensearch_engine: OpenSearchEngine, db: AsyncSession, opensearch: OpenSearch
    ):
        dataset = await DatasetFactory.create()

        await refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["settings"]["index"]["knn"] == "false"

    async def test_create_dataset_index_with_vectors(self, search_engine: OpenSearchEngine, opensearch: OpenSearch):
        vectors_settings = await VectorSettingsFactory.create_batch(5)
        dataset = await DatasetFactory.create(vectors_settings=vectors_settings)

        await refresh_dataset(dataset)
        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["vectors"]["properties"] == {
            str(settings.id): {
                "type": "knn_vector",
                "dimension": settings.dimensions,
                "method": {
                    "engine": "lucene",
                    "space_type": "cosinesimil",
                    "name": "hnsw",
                    "parameters": {"ef_construction": 4, "m": 2},
                },
            }
            for settings in vectors_settings
        }

        assert index["settings"]["index"]["knn"] == "false"

    async def test_create_index_with_existing_index(self, search_engine: OpenSearchEngine, opensearch: OpenSearch):
        dataset = await DatasetFactory.create()

        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        with pytest.raises(RequestError, match="resource_already_exists_exception"):
            await search_engine.create_index(dataset)
