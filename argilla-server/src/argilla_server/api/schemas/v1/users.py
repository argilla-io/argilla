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
from typing import Annotated, List, Optional
from uuid import UUID

from argilla_server.enums import UserRole
from argilla_server.pydantic_v1 import BaseModel, Field, constr

USER_PASSWORD_MIN_LENGTH = 8
USER_PASSWORD_MAX_LENGTH = 100

UserFirstName = Annotated[
    constr(min_length=1, strip_whitespace=True), Field(..., description="The first name for the user")
]
UserLastName = Annotated[
    constr(min_length=1, strip_whitespace=True), Field(..., description="The last name for the user")
]
UserUsername = Annotated[str, Field(..., min_length=1, description="The username for the user")]

UserPassword = Annotated[
    str,
    Field(
        ...,
        min_length=USER_PASSWORD_MIN_LENGTH,
        max_length=USER_PASSWORD_MAX_LENGTH,
        description="The password for the user",
    ),
]


class User(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str]
    username: str
    role: UserRole
    # TODO: We need to move `api_key` outside of this schema and think about a more
    # secure way to expose it, along with ways to expire it and create new API keys.
    api_key: str
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    first_name: UserFirstName
    last_name: Optional[UserLastName]
    username: UserUsername
    role: Optional[UserRole]
    password: UserPassword


class UserUpdate(BaseModel):
    first_name: Optional[UserFirstName]
    last_name: Optional[UserLastName]
    username: Optional[UserUsername]
    role: Optional[UserRole]
    password: Optional[UserPassword]


class Users(BaseModel):
    items: List[User]
