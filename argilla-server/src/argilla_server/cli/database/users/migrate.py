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
import asyncio
import os
from typing import TYPE_CHECKING, List, Optional

import typer
import yaml

from argilla_server.api.schemas.v1.users import USER_USERNAME_REGEX
from argilla_server.api.schemas.v1.workspaces import WORKSPACE_NAME_REGEX
from argilla_server.database import AsyncSessionLocal
from argilla_server.models import User, UserRole
from argilla_server.pydantic_v1 import BaseModel, Field, constr

from .utils import get_or_new_workspace

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class WorkspaceCreate(BaseModel):
    name: str = Field(..., regex=WORKSPACE_NAME_REGEX, min_length=1)


class UserCreate(BaseModel):
    first_name: constr(strip_whitespace=True)
    username: str = Field(..., regex=USER_USERNAME_REGEX, min_length=1)
    role: UserRole
    api_key: constr(min_length=1)
    password_hash: constr(min_length=1)
    workspaces: Optional[List[WorkspaceCreate]]


class UsersMigrator:
    def __init__(self, users_filename: str):
        self._users_filename = users_filename

        with open(users_filename) as users_file:
            self._users = yaml.safe_load(users_file.read())

    async def migrate(self):
        typer.echo(f"Starting users migration process using file {self._users_filename!r}")

        async with AsyncSessionLocal() as session:
            try:
                for user in self._users:
                    await self._migrate_user(session, user)
                await session.commit()
            except Exception:
                await session.rollback()
                typer.echo("Users migration process failed...")
                raise typer.Exit(code=1)

            typer.echo("Users migration process successfully finished")

    async def _migrate_user(self, session: "AsyncSession", user: dict):
        typer.echo(f"Migrating User with username {user['username']!r}")

        user_create = self._build_user_create(user)

        await User.create(
            session,
            first_name=user_create.first_name,
            username=user_create.username,
            role=user_create.role,
            api_key=user_create.api_key,
            password_hash=user_create.password_hash,
            workspaces=[await get_or_new_workspace(session, workspace.name) for workspace in user_create.workspaces],
            autocommit=False,
        )

    def _build_user_create(self, user: dict) -> UserCreate:
        return UserCreate(
            first_name=user.get("full_name", ""),
            username=user["username"],
            role=self._user_role(user),
            api_key=user["api_key"],
            password_hash=user["hashed_password"],
            workspaces=[WorkspaceCreate(name=workspace_name) for workspace_name in self._user_workspace_names(user)],
        )

    def _user_role(self, user: dict) -> UserRole:
        if user.get("workspaces") is None:
            return UserRole.owner

        return UserRole.annotator

    def _user_workspace_names(self, user: dict) -> List[str]:
        workspace_names = [workspace_name for workspace_name in user.get("workspaces", [])]

        if user["username"] in workspace_names:
            return workspace_names

        return [user["username"]] + workspace_names


def migrate():
    """Migrate users defined in YAML file to database."""

    users_db_file: str = os.getenv("ARGILLA_LOCAL_AUTH_USERS_DB_FILE", ".users.yml")
    asyncio.run(UsersMigrator(users_db_file).migrate())


if __name__ == "__main__":
    typer.run(migrate)
