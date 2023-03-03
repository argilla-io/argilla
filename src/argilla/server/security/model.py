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
import re
import uuid
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr, root_validator, validator
from pydantic.utils import GetterDict

from argilla._constants import ES_INDEX_REGEX_PATTERN
from argilla.server.errors import BadRequestError, EntityNotFoundError
from argilla.server.models import UserRole

_WORKSPACE_NAME_REGEX = ES_INDEX_REGEX_PATTERN


_USER_PASSWORD_MIN_LENGTH = 8
_USER_PASSWORD_MAX_LENGTH = 100
_USER_USERNAME_REGEX = ES_INDEX_REGEX_PATTERN


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
    name: constr(regex=_WORKSPACE_NAME_REGEX, min_length=1)


class UserCreate(BaseModel):
    first_name: constr(min_length=1, strip_whitespace=True)
    last_name: Optional[constr(min_length=1, strip_whitespace=True)]
    username: constr(regex=_USER_USERNAME_REGEX, min_length=1)
    role: Optional[UserRole]
    password: constr(min_length=_USER_PASSWORD_MIN_LENGTH, max_length=_USER_PASSWORD_MAX_LENGTH)


class UserGetter(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "full_name":
            return f"{self._obj.first_name} {self._obj.last_name}"
        elif key == "workspaces":
            return [workspace.name for workspace in self._obj.workspaces]
        else:
            return super().get(key, default)


class User(BaseModel):
    """Base user model"""

    id: UUID
    username: str = Field()
    role: UserRole
    full_name: Optional[str] = None

    superuser: Optional[bool]
    workspaces: Optional[List[str]]
    api_key: str

    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        getter_dict = UserGetter

    @root_validator()
    def check_defaults(cls, values):
        superuser = values.get("superuser")
        workspaces = values.get("workspaces")

        values["superuser"] = cls._set_default_superuser(superuser, values)
        values["workspaces"] = cls._set_default_workspace(workspaces, values)

        return values

    @classmethod
    def _set_default_superuser(cls, value, values):
        """This will setup the superuser flag when no workspaces are defined"""
        if value is not None:
            return value
        # The current way to define super-users is create them with no workspaces at all
        # (IT'S NOT THE SAME AS PASSING AN EMPTY LIST)
        return values.get("workspaces", None) is None

    @classmethod
    def _set_default_workspace(cls, value, values):
        value = (value or []).copy()
        value.append(values["username"])

        return list(set(value))

    def check_workspaces(self, workspaces: List[str]) -> List[str]:
        """
        Given a list of workspaces, apply a belongs to validation for each one. Then, return
        original list if any, else user workspaces (including private/default one)

        Parameters
        ----------
        workspaces:
            A list of workspace names

        Returns
        -------
            Original workspace names if user belongs to them

        """
        workspaces = [w for w in workspaces or [] if w is not None]
        if workspaces:
            for workspace in workspaces:
                self.check_workspace(workspace)
            return workspaces
        else:
            return self.workspaces

    def check_workspace(self, workspace: str) -> str:
        """
        Given a workspace name, check if user belongs to it, raising a error if not.

        Parameters
        ----------
        workspace:
            Workspace to check

        Returns
        -------
            The original workspace name if user belongs to it

        """
        if not workspace:
            raise BadRequestError("Missing workspace. A workspace must by provided")
        elif workspace not in self.workspaces:
            raise EntityNotFoundError(name=workspace, type="Workspace")
        return workspace

    def is_superuser(self) -> bool:
        """Check if a user is superuser"""
        return self.superuser


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
