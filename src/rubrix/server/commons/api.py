from dataclasses import dataclass

from fastapi import Header, Query


@dataclass
class CommonTaskQueryParams:
    """Common task query params"""

    __workspace_param__: str = Query(
        None,
        alias="workspace",
        description="The workspace where dataset belongs to. If not provided default user team will be used",
    )

    __workspace_header__: str = Header(None, alias="X-Rubrix-Workspace")

    @property
    def workspace(self) -> str:
        """Return read workspace. Query param prior to header param"""
        return self.__workspace_param__ or self.__workspace_header__
