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
from enum import Enum
from typing import List, Optional
from uuid import UUID

from argilla.pydantic_v1 import BaseModel, Field


class UserRole(str, Enum):
    owner = "owner"
    admin = "admin"
    annotator = "annotator"


class UserCreateModel(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: Optional[str] = Field(min_length=1)
    username: str = Field(min_length=1, regex=r"^(?!-|_)[a-z0-9-_]+$")
    role: UserRole = UserRole.annotator
    password: str = Field(min_length=8, max_length=100)
    workspaces: Optional[List[str]] = None


class UserModel(BaseModel):
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
