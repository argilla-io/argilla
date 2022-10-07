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

from dataclasses import dataclass

from fastapi import Header, Path, Query

from argilla._constants import (
    _OLD_WORKSPACE_HEADER_NAME,
    DATASET_NAME_REGEX_PATTERN,
    WORKSPACE_HEADER_NAME,
)
from argilla.server.security.model import WORKSPACE_NAME_PATTERN

DATASET_NAME_PATH_PARAM = Path(
    ..., regex=DATASET_NAME_REGEX_PATTERN, description="The dataset name"
)


@dataclass
class RequestPagination:
    """Query pagination params"""

    limit: int = Query(50, gte=0, le=1000, description="Response records limit")
    from_: int = Query(
        0, ge=0, le=10000, alias="from", description="Record sequence from"
    )


@dataclass
class CommonTaskHandlerDependencies:
    """Common task query dependencies"""

    # TODO(@frascuchon): we could include the request user and parametrize the action scopes
    #   Depends(CommonTaskHandlerDependencies.create(scopes=[...])

    __workspace_header__: str = Header(None, alias=WORKSPACE_HEADER_NAME)
    __old_workspace_header__: str = Header(
        None,
        alias=_OLD_WORKSPACE_HEADER_NAME,
        description="This is for backward comp. with old clients",
    )
    __workspace_param__: str = Query(
        None,
        alias="workspace",
        description="The workspace where dataset belongs to. If not provided default user team will be used",
    )

    @property
    def workspace(self) -> str:
        """Return read workspace. Query param prior to header param"""
        workspace = (
            self.__workspace_param__
            or self.__workspace_header__
            or self.__old_workspace_header__
        )
        if workspace:
            assert WORKSPACE_NAME_PATTERN.match(workspace), (
                "Wrong workspace format. "
                f"Workspace must match pattern {WORKSPACE_NAME_PATTERN.pattern}"
            )
        return workspace
