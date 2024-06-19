# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from typing import Optional

from pydantic import field_validator, ConfigDict

from argilla._models import ResourceModel

__all__ = ["UserModel", "Role"]


class Role(str, Enum):
    annotator = "annotator"
    admin = "admin"
    owner = "owner"


class UserModel(ResourceModel):
    username: str
    role: Role = Role.annotator

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @field_validator("first_name")
    @classmethod
    def __validate_first_name(cls, v, values):
        """Set first_name to username if not provided"""
        if isinstance(v, str):
            return v
        elif not v:
            return values["username"]

    @field_validator("username", mode="before")
    @classmethod
    def __validate_username(cls, username: str):
        """Ensure that the username is not empty"""
        if not username:
            raise ValueError("Username cannot be empty")
        return username
