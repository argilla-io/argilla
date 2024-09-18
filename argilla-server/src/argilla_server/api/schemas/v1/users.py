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

from argilla_server.enums import UserRole

# from argilla_server.pydantic_v1 import BaseModel, Field, constr
from pydantic import StringConstraints, ConfigDict, BaseModel, Field
from typing_extensions import Annotated

# Pydantic v2 error: look-around, including look-ahead and look-behind, is not supported so rewriting it:
# USER_USERNAME_REGEX = "^(?!-|_)[A-za-z0-9-_]+$"
USER_USERNAME_REGEX = r"^[A-Za-z0-9][A-Za-z0-9-_]*$"
USER_PASSWORD_MIN_LENGTH = 8
USER_PASSWORD_MAX_LENGTH = 100


class User(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str] = None
    username: str
    role: UserRole
    # TODO: We need to move `api_key` outside of this schema and think about a more
    # secure way to expose it, along with ways to expire it and create new API keys.
    api_key: str
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    last_name: Optional[Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]] = None
    username: str = Field(pattern=USER_USERNAME_REGEX, min_length=1)
    role: Optional[UserRole] = None
    password: str = Field(min_length=USER_PASSWORD_MIN_LENGTH, max_length=USER_PASSWORD_MAX_LENGTH)


class Users(BaseModel):
    items: List[User]
