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
import io
import os
from collections import OrderedDict
from sqlite3 import Connection as SQLite3Connection
from typing import Optional

import alembic.config
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.util import CommandError
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from argilla.server.settings import settings


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


TAGGED_REVISIONS = OrderedDict(
    {
        "1.7": "1769ee58fbb4",
        "1.8": "ae5522b4c674",
    }
)


def migrate_db(revision: Optional[str] = None):
    alembic_config_file = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    if revision:
        revision = TAGGED_REVISIONS.get(revision, revision)

        current_revision = _get_current_revision(alembic_config_file)
        script = ScriptDirectory.from_config(Config(alembic_config_file))

        try:
            script.walk_revisions(base=current_revision, head=revision)
            action = "upgrade"
        except CommandError:
            action = "downgrade"

    else:
        revision = "head"
        action = "upgrade"

    alembic.config.main(argv=["-c", alembic_config_file, action, revision])


def revisions(show_current: bool = True):
    alembic_config_file = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))

    alembic.config.main(argv=["-c", alembic_config_file, "history"])
    if show_current:
        print("\n")
        alembic.config.main(argv=["-c", alembic_config_file, "current", "--v"])


def _get_current_revision(alembic_config_file: str) -> str:
    output_buffer = io.StringIO()
    alembic_cfg = Config(alembic_config_file, stdout=output_buffer)

    command.current(alembic_cfg)
    return output_buffer.getvalue().strip().split(" ")[0]


class Base(DeclarativeBase):
    pass
