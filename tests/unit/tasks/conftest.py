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

from datetime import datetime
from typing import TYPE_CHECKING, Generator
from uuid import uuid4

import pytest
from argilla.__main__ import app
from argilla.client.workspaces import Workspace
from argilla.server.database import database_url_sync
from argilla.tasks.database.migrate import migrate_db
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from typer.testing import CliRunner

from tests.database import SyncTestSession

if TYPE_CHECKING:
    from argilla.tasks.async_typer import AsyncTyper
    from pytest_mock import MockerFixture
    from sqlalchemy.engine import Connection
    from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def cli() -> "AsyncTyper":
    return app


@pytest.fixture(scope="session")
def sync_connection() -> Generator["Connection", None, None]:
    engine = create_engine(database_url_sync())
    conn = engine.connect()
    SyncTestSession.configure(bind=conn)
    migrate_db("head")

    yield conn

    migrate_db("base")
    conn.close()
    engine.dispose()


@pytest.fixture(autouse=True)
def sync_db(sync_connection: "Connection") -> Generator["Session", None, None]:
    sync_connection.begin_nested()
    session = SyncTestSession()

    yield session

    session.close()
    SyncTestSession.remove()
    sync_connection.rollback()


@pytest.fixture
def async_db_proxy(mocker: "MockerFixture", sync_db: "Session") -> "AsyncSession":
    """Create a mocked `AsyncSession` that proxies to the sync session. This will allow us to execute the async CLI commands
    and then in the unit test function use the sync session to assert the changes.

    Args:
        mocker: pytest-mock fixture.
        sync_db: Sync session.

    Returns:
        Mocked `AsyncSession` that proxies to the sync session.
    """
    async_session = AsyncSession()
    async_session.sync_session = sync_db
    async_session._proxied = sync_db
    async_session.close = mocker.AsyncMock()

    return async_session


@pytest.fixture
def login_mock(mocker: "MockerFixture") -> None:
    mocker.patch("argilla.client.login.ArgillaCredentials.exists", return_value=True)
    mocker.patch("argilla.client.api.ArgillaSingleton.init")


@pytest.fixture
def not_logged_mock(mocker: "MockerFixture") -> None:
    mocker.patch("argilla.client.login.ArgillaCredentials.exists", return_value=False)


@pytest.fixture
def workspace() -> Workspace:
    workspace = Workspace.__new__(Workspace)
    workspace.__dict__.update(
        {
            "id": uuid4(),
            "name": "unit-test",
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )
    return workspace
