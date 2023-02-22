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

import httpx
import pytest
from _pytest.logging import LogCaptureFixture
from argilla._constants import API_KEY_HEADER_NAME, DEFAULT_API_KEY
from argilla.client.client import Argilla
from argilla.client.sdk.users import api as users_api
from argilla.server.commons import telemetry
from argilla.server.database import SessionLocal
from argilla.server.models import User, Workspace
from argilla.server.seeds import test_seeds

try:
    from loguru import logger
except ModuleNotFoundError:
    logger = None
from argilla import app
from argilla.client.api import active_api
from starlette.testclient import TestClient

from .helpers import SecuredClient


@pytest.fixture(scope="session")
def api_key_header():
    return {API_KEY_HEADER_NAME: DEFAULT_API_KEY}


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db():
    test_seeds()
    session = SessionLocal()

    yield session

    session.query(User).delete()
    session.query(Workspace).delete()
    session.commit()


@pytest.fixture
def telemetry_track_data(mocker):
    client = telemetry._TelemetryClient.get()
    if client:
        # Disable sending data for tests
        client.client = telemetry._configure_analytics(disable_send=True)
        spy = mocker.spy(client, "track_data")

        return spy


@pytest.fixture
def mock_user(db):
    user = User(
        first_name="Mock",
        username="mock-user",
        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
        api_key="mock-user.apikey",
        workspaces=[Workspace(name="argilla"), Workspace(name="mock-ws")],
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def api():
    return Argilla()


@pytest.fixture
def mocked_client(
    db,
    monkeypatch,
    telemetry_track_data,
) -> SecuredClient:
    with TestClient(app, raise_server_exceptions=False) as _client:
        client_ = SecuredClient(_client)

        real_whoami = users_api.whoami

        def whoami_mocked(client):
            monkeypatch.setattr(client, "__httpx__", client_)
            return real_whoami(client)

        monkeypatch.setattr(users_api, "whoami", whoami_mocked)

        monkeypatch.setattr(httpx, "post", client_.post)
        monkeypatch.setattr(httpx, "patch", client_.patch)
        monkeypatch.setattr(httpx.AsyncClient, "post", client_.post_async)
        monkeypatch.setattr(httpx, "get", client_.get)
        monkeypatch.setattr(httpx, "delete", client_.delete)
        monkeypatch.setattr(httpx, "put", client_.put)
        monkeypatch.setattr(httpx, "stream", client_.stream)

        rb_api = active_api()
        monkeypatch.setattr(rb_api._client, "__httpx__", client_)

        yield client_


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    if not logger:
        yield caplog
    else:
        handler_id = logger.add(caplog.handler, format="{message}")
        yield caplog
        logger.remove(handler_id)
