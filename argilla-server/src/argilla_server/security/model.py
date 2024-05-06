#  coding=utf-8
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
from typing import Any, List, Optional
from uuid import UUID

from argilla_server.constants import ES_INDEX_REGEX_PATTERN
from argilla_server.models import UserRole
from argilla_server.pydantic_v1 import BaseModel, Field, constr
from argilla_server.pydantic_v1.utils import GetterDict

WORKSPACE_NAME_REGEX = ES_INDEX_REGEX_PATTERN

USER_USERNAME_REGEX = ES_INDEX_REGEX_PATTERN
USER_PASSWORD_MIN_LENGTH = 8
USER_PASSWORD_MAX_LENGTH = 100


class WorkspaceUserCreate(BaseModel):
    user_id: UUID
    workspace_id: UUID


class Workspace(BaseModel):
    id: UUID
    name: str
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WorkspaceCreate(BaseModel):
    name: str = Field(..., regex=WORKSPACE_NAME_REGEX, min_length=1)


class UserCreate(BaseModel):
    first_name: constr(min_length=1, strip_whitespace=True)
    last_name: Optional[constr(min_length=1, strip_whitespace=True)]
    username: str = Field(regex=USER_USERNAME_REGEX, min_length=1)
    role: Optional[UserRole]
    password: constr(min_length=USER_PASSWORD_MIN_LENGTH, max_length=USER_PASSWORD_MAX_LENGTH)
    workspaces: Optional[List[str]]


class UserGetter(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "full_name":
            return f"{self._obj.first_name} {self._obj.last_name}" if self._obj.last_name else self._obj.first_name
        elif key == "workspaces":
            return [workspace.name for workspace in self._obj.workspaces]
        else:
            return super().get(key, default)


class User(BaseModel):
    """Base user model"""

    id: UUID
    first_name: str
    last_name: Optional[str]
    full_name: Optional[str] = Field(description="Deprecated. Use `first_name` and `last_name` instead")
    username: str = Field()
    role: UserRole
    workspaces: Optional[List[str]]
    api_key: str
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        getter_dict = UserGetter


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
