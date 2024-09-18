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

from typing import TYPE_CHECKING

from sqlalchemy import select

from argilla_server.models import Workspace

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_new_workspace(session: "AsyncSession", workspace_name: str) -> Workspace:
    result = await session.execute(select(Workspace).filter_by(name=workspace_name))
    workspace = result.scalar_one_or_none()
    return workspace or Workspace(name=workspace_name)
