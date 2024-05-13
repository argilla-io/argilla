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
from typing import Union

from sqlalchemy import orm
from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker

task: Union[asyncio.Task, None] = None


def set_task(t: asyncio.Task):
    global task
    task = t


def get_task() -> asyncio.Task:
    return task


TestSession = async_scoped_session(async_sessionmaker(expire_on_commit=False, future=True), get_task)
SyncTestSession = orm.scoped_session(orm.sessionmaker(class_=orm.Session, expire_on_commit=False))
