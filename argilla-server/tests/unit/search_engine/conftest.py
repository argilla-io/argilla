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

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from argilla_server.search_engine import ElasticSearchEngine, OpenSearchEngine
from argilla_server.settings import settings


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
