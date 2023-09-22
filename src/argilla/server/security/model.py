from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr
from pydantic.utils import GetterDict

from argilla._constants import ES_INDEX_REGEX_PATTERN
from argilla.server.enums import UserRole

USER_USERNAME_REGEX = ES_INDEX_REGEX_PATTERN
USER_PASSWORD_MIN_LENGTH = 8
USER_PASSWORD_MAX_LENGTH = 100


class UserCreate(BaseModel):
    first_name: constr(min_length=1, strip_whitespace=True)
    last_name: Optional[constr(min_length=1, strip_whitespace=True)]
    username: constr(regex=USER_USERNAME_REGEX, min_length=1)
    role: Optional[UserRole]
    password: constr(min_length=USER_PASSWORD_MIN_LENGTH, max_length=USER_PASSWORD_MAX_LENGTH)
    workspaces: Optional[List[str]]


class UserGetter(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "full_name":
            return f"{self._obj.first_name} {self._obj.last_name}" if self._obj.last_name else self._obj.first_name
        elif key == "workspaces":
            return [workspace.name for workspace in self._obj.workspaces]
        else:
            return super().get(key, default)


class User(BaseModel):
    """Base user model"""

    id: UUID
    first_name: str
    last_name: Optional[str]
    full_name: Optional[str] = Field(description="Deprecated. Use `first_name` and `last_name` instead")
    username: str = Field()
    role: UserRole
    workspaces: Optional[List[str]]
    api_key: str
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        getter_dict = UserGetter


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
    name: constr(regex=WORKSPACE_NAME_REGEX, min_length=1)
