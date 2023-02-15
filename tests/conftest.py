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
from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from argilla.client.client import Argilla
from argilla.client.sdk.users import api as users_api
from argilla.server.commons import telemetry
from argilla.server.database import Base, SessionLocal
from argilla.server.models import User, Workspace

try:
    from loguru import logger
except ModuleNotFoundError:
    logger = None
from starlette.testclient import TestClient

from argilla import app
from argilla.client.api import active_api

from .helpers import SecuredClient


@pytest.fixture
def telemetry_track_data(mocker):
    client = telemetry._TelemetryClient.get()
    if client:
        # Disable sending data for tests
        client.client = telemetry._configure_analytics(disable_send=True)
        spy = mocker.spy(client, "track_data")

        return spy


@pytest.fixture(scope="session")
def engine():
    from argilla.server.database import engine

    return engine


@pytest.fixture(scope="session")
def setup_database(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed_for_tests()

    yield engine

    Base.metadata.drop_all(engine)


def seed_for_tests():
    with SessionLocal() as db_session:
        db_session.add_all(
            [
                User(
                    first_name="Argilla",
                    username="argilla",
                    email="ar@argilla.io",
                    password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
                    api_key="argilla.apikey",
                    workspaces=[
                        Workspace(name=""),
                        Workspace(name="argilla"),
                        Workspace(name="my-fun-workspace"),
                    ],
                ),
                User(
                    username="mock-user",
                    email="mock-user@argilla.io",
                    password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
                    api_key="mock-user.apikey",
                    workspaces=[Workspace(name="argilla"), Workspace(name="mock-ws")],
                ),
            ]
        )

        db_session.commit()


@pytest.fixture
def db_session(setup_database, engine):
    connection = engine.connect()
    transaction = connection.begin()

    yield scoped_session(SessionLocal)

    transaction.rollback()


@pytest.fixture
def mock_user(db_session):
    user = db_session.scalar(select(User).where(User.username == "mock-user"))

    return user


@pytest.fixture
def api():
    return Argilla()


@pytest.fixture
def mocked_client(
    db_session,
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
