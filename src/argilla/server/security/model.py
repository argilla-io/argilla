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
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from argilla._constants import DATASET_NAME_REGEX_PATTERN
from argilla.server.errors import EntityNotFoundError

WORKSPACE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-]*$")
_EMAIL_REGEX_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"


class User(BaseModel):
    """Base user model"""

    username: str = Field()
    email: Optional[str] = Field(None, regex=_EMAIL_REGEX_PATTERN)
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    # This order is important since we want execute superuser validator prior to workspace validators
    superuser: Optional[bool]
    workspaces: Optional[List[str]]

    @validator("username")
    def check_username(cls, value):
        if not re.compile(DATASET_NAME_REGEX_PATTERN).match(value):
            raise ValueError(
                "Wrong username. " f"The username {value} does not match the pattern {DATASET_NAME_REGEX_PATTERN}"
            )
        return value

    @validator("workspaces", each_item=True)
    def check_workspace_pattern(cls, workspace: str):
        """Check workspace pattern"""
        if not workspace:
            return workspace
        assert WORKSPACE_NAME_PATTERN.match(workspace), (
            "Wrong workspace format. " f"Workspace must match pattern {WORKSPACE_NAME_PATTERN.pattern}"
        )
        return workspace

    @root_validator
    def check_defaults(cls, values):
        values["superuser"] = cls._set_default_superuser(values.get("superuser"), values)
        values["workspaces"] = cls._set_default_workspace(values.get("set_default_workspace"))

        return values

    @classmethod
    def _set_default_superuser(cls, value, values):
        """This will setup the superuser flag when no workspaces are defined"""
        if value is not None:
            return value
        return values.get("workspaces", None) is None

    @classmethod
    def _set_default_workspace(cls, value):
        if value is None:
            return []
        return value

    @property
    def available_workspaces(self) -> List[str]:
        """Return a list of available workspaces for current user.
        Even if self.workspaces is None, this method will return the default workspace
        corresponding to the user username.
        """
        workspaces = set((self.workspaces or []) + [self.default_workspace])
        return list(workspaces)

    @property
    def default_workspace(self) -> Optional[str]:
        """Get the default user workspace"""
        return self.username

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
            return self.available_workspaces

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
        if workspace is None or workspace == self.default_workspace:
            return self.default_workspace
        if not workspace and self.is_superuser():
            return workspace
        if workspace not in self.available_workspaces:
            raise EntityNotFoundError(name=workspace, type="Workspace")
        return workspace

    def is_superuser(self) -> bool:
        """Check if a user is superuser"""
        return self.superuser


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
