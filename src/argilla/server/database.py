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

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import argilla
from argilla.server.settings import settings
from argilla.utils.utils import is_unit_test

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

ALEMBIC_CONFIG_FILE = os.path.normpath(os.path.join(os.path.dirname(argilla.__file__), "alembic.ini"))
TAGGED_REVISIONS = OrderedDict({"1.7": "1769ee58fbb4", "1.8": "ae5522b4c674"})


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(settings.database_url_async)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=async_engine, class_=AsyncSession
)


def get_db() -> Generator["Session", None, None]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_async_db() -> Generator["AsyncSession", None, None]:
    try:
        db: "AsyncSession" = AsyncSessionLocal()
        yield db
    finally:
        await db.close()


class Base(AsyncAttrs, DeclarativeBase):
    def __eq__(self, value: object) -> bool:
        if is_unit_test():
            return self.id == value.id
        return super().__eq__(value)
