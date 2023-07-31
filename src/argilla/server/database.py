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
from sqlite3 import Connection as SQLite3Connection
from typing import TYPE_CHECKING, Generator

from sqlalchemy import event, make_url
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import argilla
from argilla.server.settings import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


ALEMBIC_CONFIG_FILE = os.path.normpath(os.path.join(os.path.dirname(argilla.__file__), "alembic.ini"))
TAGGED_REVISIONS = OrderedDict(
    {
        "1.7": "1769ee58fbb4",
        "1.8": "ae5522b4c674",
        "1.11": "3ff6484f8b37",
        "1.13": "1e629a913727",
    }
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async_engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(autocommit=False, expire_on_commit=False, bind=async_engine)


async def get_async_db() -> Generator["AsyncSession", None, None]:
    try:
        db: "AsyncSession" = AsyncSessionLocal()
        yield db
    finally:
        await db.close()


def database_url_sync() -> str:
    """
    Returns a "sync" version of the configured database URL. This may be useful in cases we don't need
    an asynchronous connection, like running database migration inside the alembic script.
    """
    database_url = make_url(settings.database_url)
    return settings.database_url.replace(f"+{database_url.get_driver_name()}", "")
