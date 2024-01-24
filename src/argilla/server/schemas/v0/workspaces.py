from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from argilla.server.constants import ES_INDEX_REGEX_PATTERN

WORKSPACE_NAME_REGEX = ES_INDEX_REGEX_PATTERN


class WorkspaceUserCreate(BaseModel):
    user_id: UUID
    workspace_id: UUID


class Workspace(BaseModel):
    id: UUID
    name: str
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WorkspaceCreate(BaseModel):
    name: str = Field(..., regex=WORKSPACE_NAME_REGEX, min_length=1)
