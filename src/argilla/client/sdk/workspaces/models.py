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
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from argilla.client.sdk.users.models import UserRole


class WorkspaceModel(BaseModel):
    id: UUID
    name: str
    inserted_at: datetime
    updated_at: datetime


# TODO(alvarobartt): replace with the `pydantic.BaseModel` created at https://github.com/argilla-io/argilla/pull/3169 once is merged
class WorkspaceUserModel(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str]
    full_name: Optional[str]
    username: str
    role: UserRole
    workspaces: Optional[List[str]]
    api_key: str
    inserted_at: datetime
    updated_at: datetime
