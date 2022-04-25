from dataclasses import dataclass
from typing import Type

from fastapi import Header, Path, Query

from rubrix.server.apis.v1.constants import (
    DATASET_NAME_PATTERN,
    RUBRIX_WORKSPACE_HEADER_NAME,
    WORKSPACE_NAME_PATTERN,
)

TASK_TYPE_PATH_PARAM = Path(..., description="The dataset task type")
DATASET_NAME_PATH_PARAM = Path(
    ..., description="The dataset name", regex=DATASET_NAME_PATTERN
)

__WS_DESCRIPTION__ = "The workspace where dataset belongs to. If not provided default user workspace will be used"
WORKSPACE_QUERY_PARAM = Query(
    None,
    alias="workspace",
    description=__WS_DESCRIPTION__,
)
WORKSPACE_HEADER_PARAM = Header(
    None, description=__WS_DESCRIPTION__, alias=RUBRIX_WORKSPACE_HEADER_NAME
)


@dataclass
class WorkspaceParams:

    __workspace_query__: str = WORKSPACE_QUERY_PARAM
    __workspace_header__: str = WORKSPACE_HEADER_PARAM

    @property
    def workspace(self) -> str:
        """Return read workspace. Query param prior to header param"""
        workspace = self.__workspace_query__ or self.__workspace_header__
        if workspace:
            assert WORKSPACE_NAME_PATTERN.match(workspace), (
                "Wrong workspace format. "
                f"Workspace must match pattern {WORKSPACE_NAME_PATTERN.pattern}"
            )
        return workspace


def build_pagination_params(item_type: str) -> Type:
    @dataclass()
    class PaginationParams:
        limit: int = Query(
            50,
            gte=0,
            le=1000,
            description=f"Limit the number of {item_type.title()}s to return",
        )
        from_: int = Query(
            0,
            ge=0,
            le=10000,
            alias="from",
            description=f"Number of {item_type.title()}s  to skip before returning results",
        )

    return PaginationParams
