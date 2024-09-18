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

import asyncio
from typing import TYPE_CHECKING, AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio
from argilla_server.cli.database.migrate import migrate_db
from argilla_server.database import database_url_sync
from argilla_server.settings import settings
from sqlalchemy import NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from tests.database import SyncTestSession, TestSession, set_task

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from sqlalchemy.ext.asyncio import AsyncConnection


@pytest.fixture(scope="session")
def event_loop() -> Generator["asyncio.AbstractEventLoop", None, None]:
    loop = asyncio.get_event_loop_policy().get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def mock_httpx_client(mocker) -> Generator[httpx.Client, None, None]:
    return mocker.Mock(httpx.Client)


@pytest_asyncio.fixture(scope="session")
async def connection() -> AsyncGenerator["AsyncConnection", None]:
    set_task(asyncio.current_task())
    database_url = settings.database_url
    engine = create_async_engine(database_url, poolclass=NullPool)
    conn = await engine.connect()
    TestSession.configure(bind=conn)
    migrate_db("head")

    yield conn

    migrate_db("base")
    await conn.close()
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def db(connection: "AsyncConnection") -> AsyncGenerator["AsyncSession", None]:
    await connection.begin_nested()
    session = TestSession()

    yield session

    await session.close()
    await TestSession.remove()
    await connection.rollback()


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
