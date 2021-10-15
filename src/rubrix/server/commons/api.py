from dataclasses import dataclass

from fastapi import Query


@dataclass
class TeamsQueryParams:
    """Common team query params"""

    team: str = Query(
        None,
        description="The team where dataset belongs to. If not provided default user team will be used",
    )
