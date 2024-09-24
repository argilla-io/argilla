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

import uuid
from typing import TYPE_CHECKING, Dict, Generator, Optional

import pytest
import pytest_asyncio
from sqlalchemy.engine.interfaces import IsolationLevel
from httpx import AsyncClient
from opensearchpy import OpenSearch

from argilla_server import telemetry
from argilla_server.contexts import distribution, datasets, records
from argilla_server.api.routes import api_v1
from argilla_server.constants import API_KEY_HEADER_NAME, DEFAULT_API_KEY
from argilla_server.database import get_async_db
from argilla_server.models import User, UserRole, Workspace
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.settings import settings
from argilla_server.telemetry import TelemetryClient
from tests.database import TestSession
from tests.factories import AnnotatorFactory, OwnerFactory, UserFactory

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture(scope="session")
def elasticsearch_config():
    return {"hosts": settings.elasticsearch}


@pytest.fixture(scope="session", autouse=True)
def opensearch(elasticsearch_config: dict) -> Generator[OpenSearch, None, None]:
    client = OpenSearch(**elasticsearch_config)
    yield client

    for index_info in client.cat.indices(index="ar.*,rg.*", format="json"):
        client.indices.delete(index=index_info["index"])


@pytest.fixture(scope="function")
def mock_search_engine(mocker) -> Generator["SearchEngine", None, None]:
    return mocker.AsyncMock(SearchEngine)


@pytest_asyncio.fixture(scope="function")
async def owner() -> User:
    return await OwnerFactory.create(first_name="Owner", username="owner", api_key="owner.apikey")


@pytest_asyncio.fixture(scope="function")
async def annotator() -> User:
    return await AnnotatorFactory.create(first_name="Annotator", username="annotator", api_key="annotator.apikey")


@pytest.fixture(scope="function")
def owner_auth_header(owner: User) -> Dict[str, str]:
    return {API_KEY_HEADER_NAME: owner.api_key}


@pytest_asyncio.fixture(scope="function")
async def async_client(
    request, mock_search_engine: SearchEngine, mocker: "MockerFixture"
) -> Generator["AsyncClient", None, None]:
    from argilla_server import app

    async def override_get_async_db(isolation_level: Optional[IsolationLevel] = None):
        session = TestSession()

        # NOTE: We are ignoring the isolation_level because is causing errors with the tests.
        # if isolation_level is not None:
        #     await session.connection(execution_options={"isolation_level": isolation_level})

        yield session

    async def override_get_search_engine():
        yield mock_search_engine

    mocker.patch.object(distribution, "_get_async_db", override_get_async_db)
    mocker.patch.object(datasets, "get_async_db", override_get_async_db)
    mocker.patch.object(records, "get_async_db", override_get_async_db)

    api_v1.dependency_overrides.update(
        {
            get_async_db: override_get_async_db,
            get_search_engine: override_get_search_engine,
        }
    )

    async with AsyncClient(app=app, base_url="http://testserver") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def test_telemetry(mocker: "MockerFixture") -> "TelemetryClient":
    # Create a real instance TelemetryClient
    real_telemetry = TelemetryClient()

    # Create a wrapper to track calls to other methods
    for attr_name in dir(real_telemetry):
        attr = getattr(real_telemetry, attr_name)
        if callable(attr) and not attr_name.startswith("__"):
            wrapped = mocker.Mock(wraps=attr)
            setattr(real_telemetry, attr_name, wrapped)

    # Patch the _TELEMETRY_CLIENT to use the real_telemetry
    mocker.patch("argilla_server.telemetry._client._TELEMETRY_CLIENT", new=real_telemetry)

    return real_telemetry


@pytest_asyncio.fixture(scope="function")
async def argilla_user() -> Generator[User, None, None]:
    user = await UserFactory.create(
        first_name="Argilla",
        username="argilla",
        role=UserRole.admin,  # Force to use an admin user
        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
        api_key=DEFAULT_API_KEY,
        workspaces=[Workspace(name="argilla")],
    )
    yield user
