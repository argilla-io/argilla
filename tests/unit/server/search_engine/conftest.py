from typing import AsyncGenerator

import pytest
import pytest_asyncio

from argilla.server.search_engine import ElasticSearchEngine, OpenSearchEngine
from argilla.server.settings import settings


@pytest.fixture
def search_engine(request):
    if settings.search_engine == "elasticsearch":
        engine = "elasticsearch_engine"
    elif settings.search_engine == "opensearch":
        engine = "opensearch_engine"
    else:
        raise Exception(f"Unknown search engine: {settings.search_engine}")

    return request.getfixturevalue(engine)


@pytest_asyncio.fixture()
async def elasticsearch_engine(elasticsearch_config: dict) -> AsyncGenerator[ElasticSearchEngine, None]:
    engine = ElasticSearchEngine(config=elasticsearch_config, number_of_replicas=0, number_of_shards=1)
    yield engine

    await engine.client.close()


@pytest_asyncio.fixture()
async def opensearch_engine(elasticsearch_config: dict) -> AsyncGenerator[OpenSearchEngine, None]:
    engine = OpenSearchEngine(config=elasticsearch_config, number_of_replicas=0, number_of_shards=1)
    yield engine

    await engine.client.close()
