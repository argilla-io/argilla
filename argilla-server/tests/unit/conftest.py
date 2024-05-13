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

import contextlib
import uuid
from typing import TYPE_CHECKING, Dict, Generator

import pytest
import pytest_asyncio
from argilla_server import telemetry
from argilla_server.apis.routes import api_v0, api_v1
from argilla_server.constants import API_KEY_HEADER_NAME, DEFAULT_API_KEY
from argilla_server.daos.backend import GenericElasticEngineBackend
from argilla_server.daos.datasets import DatasetsDAO
from argilla_server.daos.records import DatasetRecordsDAO
from argilla_server.database import get_async_db
from argilla_server.models import User, UserRole, Workspace
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.settings import settings
from argilla_server.telemetry import TelemetryClient
from httpx import AsyncClient
from opensearchpy import OpenSearch

from tests.database import TestSession
from tests.factories import AnnotatorFactory, OwnerFactory, UserFactory

if TYPE_CHECKING:
    from unittest.mock import MagicMock

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


@pytest.fixture(scope="session")
def es():
    return GenericElasticEngineBackend.get_instance()


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

    async def override_get_async_db():
        session = TestSession()
        yield session

    async def override_get_search_engine():
        yield mock_search_engine

    mocker.patch("argilla_server._app._get_db_wrapper", wraps=contextlib.asynccontextmanager(override_get_async_db))

    for api in [api_v0, api_v1]:
        api.dependency_overrides[get_async_db] = override_get_async_db
        api.dependency_overrides[get_search_engine] = override_get_search_engine

    async with AsyncClient(app=app, base_url="http://testserver") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def test_telemetry(mocker: "MockerFixture") -> "MagicMock":
    mock_telemetry = mocker.Mock(TelemetryClient)
    mock_telemetry.server_id = uuid.uuid4()

    telemetry._CLIENT = mock_telemetry
    return telemetry._CLIENT


@pytest.fixture(scope="session")
def records_dao(es: GenericElasticEngineBackend):
    return DatasetRecordsDAO.get_instance(es)


@pytest.fixture(scope="session")
def datasets_dao(records_dao: DatasetRecordsDAO, es: GenericElasticEngineBackend):
    return DatasetsDAO.get_instance(es=es, records_dao=records_dao)


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
