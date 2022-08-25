from dataclasses import dataclass

from fastapi import Header, Path, Query

from rubrix._constants import DATASET_NAME_REGEX_PATTERN, RUBRIX_WORKSPACE_HEADER_NAME
from rubrix.server.security.model import WORKSPACE_NAME_PATTERN

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

    __workspace_header__: str = Header(None, alias=RUBRIX_WORKSPACE_HEADER_NAME)
    __workspace_param__: str = Query(
        None,
        alias="workspace",
        description="The workspace where dataset belongs to. If not provided default user team will be used",
    )

    @property
    def workspace(self) -> str:
        """Return read workspace. Query param prior to header param"""
        workspace = self.__workspace_param__ or self.__workspace_header__
        if workspace:
            assert WORKSPACE_NAME_PATTERN.match(workspace), (
                "Wrong workspace format. "
                f"Workspace must match pattern {WORKSPACE_NAME_PATTERN.pattern}"
            )
        return workspace
