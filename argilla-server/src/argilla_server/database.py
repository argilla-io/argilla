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

import os

from collections import OrderedDict
from typing import AsyncGenerator, Optional, Generator

from sqlalchemy import create_engine, event, make_url
from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import IsolationLevel
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from argilla_server.settings import settings

import argilla_server


ALEMBIC_CONFIG_FILE = os.path.normpath(os.path.join(os.path.dirname(argilla_server.__file__), "alembic.ini"))
TAGGED_REVISIONS = OrderedDict(
    {
        "1.7": "1769ee58fbb4",
        "1.8": "ae5522b4c674",
        "1.11": "3ff6484f8b37",
        "1.13": "1e629a913727",
        "1.17": "84f6b9ff6076",
        "1.18": "bda6fe24314e",
        "1.28": "ca7293c38970",
        "2.0": "237f7c674d74",
        "2.4": "660d6c6b3360",
        "2.5": "580a6553186f",
    }
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.database_is_sqlite:
        cursor = dbapi_connection.cursor()

        # Enforce foreign key constraints
        # https://www.sqlite.org/pragma.html#pragma_foreign_keys
        # https://www.sqlite.org/foreignkeys.html
        cursor.execute("PRAGMA foreign_keys = ON")

        # Journal mode WAL allows for greater concurrency (many readers + one writer)
        # https://www.sqlite.org/pragma.html#pragma_journal_mode
        cursor.execute("PRAGMA journal_mode = WAL")

        # Set more relaxed level of database durability
        # 2 = "FULL" (sync on every write), 1 = "NORMAL" (sync every 1000 written pages) and 0 = "NONE"
        # https://www.sqlite.org/pragma.html#pragma_synchronous
        cursor.execute("PRAGMA synchronous = NORMAL")

        # Set the global memory map so all processes can share some data
        # https://www.sqlite.org/pragma.html#pragma_mmap_size
        # https://www.sqlite.org/mmap.html
        cursor.execute("PRAGMA mmap_size = 134217728")  # 128 megabytes

        # Impose a limit on the WAL file to prevent unlimited growth
        # https://www.sqlite.org/pragma.html#pragma_journal_size_limit
        cursor.execute("PRAGMA journal_size_limit = 67108864")  # 64 megabytes

        # Set the local connection cache to 2000 pages
        # https://www.sqlite.org/pragma.html#pragma_cache_size
        cursor.execute("PRAGMA cache_size = 2000")

        cursor.close()


def database_url_sync() -> str:
    """
    Returns a "sync" version of the configured database URL. This may be useful in cases we don't need
    an asynchronous connection, like running database migration inside the alembic script.
    """
    database_url = make_url(settings.database_url)
    return settings.database_url.replace(f"+{database_url.get_driver_name()}", "")


sync_engine = create_engine(database_url_sync(), **settings.database_engine_args)

async_engine = create_async_engine(settings.database_url, **settings.database_engine_args)

SyncSessionLocal = scoped_session(sessionmaker(autocommit=False, expire_on_commit=False, bind=sync_engine))

AsyncSessionLocal = async_sessionmaker(autocommit=False, expire_on_commit=False, bind=async_engine)


def get_sync_db() -> Generator[Session, None, None]:
    db = SyncSessionLocal()

    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async for db in _get_async_db():
        yield db


async def _get_async_db(isolation_level: Optional[IsolationLevel] = None) -> AsyncGenerator[AsyncSession, None]:
    db: AsyncSession = AsyncSessionLocal()

    if isolation_level is not None:
        await db.connection(execution_options={"isolation_level": isolation_level})

    try:
        yield db
    finally:
        await db.close()
