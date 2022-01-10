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

from pydantic import BaseModel, Field, validator

from rubrix.server.commons.errors import ForbiddenOperationError


_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-]*$")
_EMAIL_REGEX_PATTERN = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"


class User(BaseModel):
    """Base user model"""

    username: str = Field(regex=_ID_REGEX.pattern)
    email: Optional[str] = Field(None, regex=_EMAIL_REGEX_PATTERN)
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    workspaces: Optional[List[str]] = None

    @validator("workspaces", each_item=True)
    def check_workspace_pattern(cls, workspace: str):
        assert _ID_REGEX.match(
            workspace
        ), f"Wrong workspace format. Workspace must match pattern {_ID_REGEX.pattern}"
        return workspace

    @property
    def default_workspace(self) -> Optional[str]:
        if self.workspaces is None:
            return None
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
        workspaces = [w for w in workspaces or [] if w]
        if workspaces:
            for workspace in workspaces:
                self.check_workspace(workspace)
            return workspaces

        if self.workspaces is None:  # Super user
            return []
        return [self.default_workspace]

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
        if not workspace or workspace == self.default_workspace:
            return self.default_workspace
        if self.workspaces is None:
            return workspace
        if workspace not in self.workspaces:
            raise ForbiddenOperationError(f"Missing or protected workspace {workspace}")
        return workspace


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
