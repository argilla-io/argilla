from dataclasses import dataclass

from fastapi import Query


@dataclass
class WorkspaceQueryParams:
    """Common team query params"""

    workspace: str = Query(
        None,
        description="The workspace where dataset belongs to. If not provided default user team will be used",
    )
