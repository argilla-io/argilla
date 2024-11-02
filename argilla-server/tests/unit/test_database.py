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

import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects import sqlite
from sqlalchemy.sql.expression import text


@pytest.mark.asyncio
class TestDatabase:
    async def test_sqlite_pragma_settings(self, db: AsyncSession):
        if db.bind.dialect.name != sqlite.dialect.name:
            return

        assert (await db.execute(text("PRAGMA foreign_keys"))).scalar() == 1
