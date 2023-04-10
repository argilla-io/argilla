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
    ES_INDEX_REGEX_PATTERN,
    WORKSPACE_HEADER_NAME,
)
from argilla.server.errors import BadRequestError, MissingInputParamError

DATASET_NAME_PATH_PARAM = Path(..., regex=ES_INDEX_REGEX_PATTERN, description="The dataset name")


@dataclass
class RequestPagination:
    """Query pagination params"""

    limit: int = Query(50, gte=0, le=1000, description="Response records limit")
    from_: int = Query(0, ge=0, le=10000, alias="from", description="Record sequence from")


@dataclass
class OptionalWorkspaceRequestDependency:
    """Common task query dependencies"""

    _description = (
        "The workspace where dataset belongs to. A valid workspace name should be provided. "
        "If not provided, the request will raise a 400 response error."
    )

    __workspace_header__: str = Header(None, alias=WORKSPACE_HEADER_NAME, deprecated=True, description=_description)

    __workspace_param__: str = Query(None, alias="workspace", description=_description)

    @property
    def workspace(self) -> str:
        """Return read workspace. Query param prior to header param"""
        return self.__workspace_param__ or self.__workspace_header__


@dataclass
class CommonTaskHandlerDependencies(OptionalWorkspaceRequestDependency):
    @property
    def workspace(self) -> str:
        workspace = super().workspace
        if not workspace:
            raise MissingInputParamError("A workspace must be provided")
        return workspace
