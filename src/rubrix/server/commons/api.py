from dataclasses import dataclass

from fastapi import Header, Query

from rubrix._constants import RUBRIX_WORKSPACE_HEADER_NAME
from rubrix.server.security.model import WORKSPACE_NAME_PATTERN


@dataclass
class CommonTaskQueryParams:
    """Common task query params"""

    __workspace_param__: str = Query(
        None,
        alias="workspace",
        description="The workspace where dataset belongs to. If not provided default user team will be used",
        regex=WORKSPACE_NAME_PATTERN.pattern,
    )

    __workspace_header__: str = Header(
        None, alias=RUBRIX_WORKSPACE_HEADER_NAME, regex=WORKSPACE_NAME_PATTERN.pattern
    )

    @property
    def workspace(self) -> str:
        """Return read workspace. Query param prior to header param"""
        return self.__workspace_param__ or self.__workspace_header__
