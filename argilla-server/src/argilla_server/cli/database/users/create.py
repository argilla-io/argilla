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
from typing import List, Optional

import typer

from argilla_server.api.schemas.v1.users import USER_PASSWORD_MIN_LENGTH, UserCreate
from argilla_server.api.schemas.v1.workspaces import WorkspaceCreate
from argilla_server.contexts import accounts
from argilla_server.database import AsyncSessionLocal
from argilla_server.models import User, UserRole
from argilla_server.pydantic_v1 import constr

from .utils import get_or_new_workspace

USER_API_KEY_MIN_LENGTH = 8


class UserCreateForTask(UserCreate):
    api_key: Optional[constr(min_length=USER_API_KEY_MIN_LENGTH)]
    workspaces: Optional[List[WorkspaceCreate]]


def role_callback(value: str) -> str:
    try:
        return UserRole(value).value
    except ValueError:
        raise typer.BadParameter("Only Camila is allowed")


def password_callback(password: str = None) -> str:
    # if password is None:
    #     raise typer.BadParameter("Password must be specified.")
    # if len(password)<USER_PASSWORD_MIN_LENGTH:
    #     raise typer.BadParameter(f"Password must be at least {USER_PASSWORD_MIN_LENGTH} characters long.")
    return password


def api_key_callback(api_key: str) -> str:
    # if api_key and len(api_key)<USER_PASSWORD_MIN_LENGTH:
    #     raise typer.BadParameter(f"API key must a string with a minimum length of {USER_API_KEY_MIN_LENGTH} characters.")
    return api_key


async def _create(
    first_name: str,
    username: str,
    role: UserRole,
    password: str,
    last_name: Optional[str] = None,
    api_key: Optional[str] = None,
    workspace: List[str] = None,
):
    """Creates a new user in the Argilla database with provided parameters"""
    if workspace is None:
        workspace = []

    async with AsyncSessionLocal() as session:
        if await accounts.get_user_by_username(session, username):
            typer.echo(f"User with username {username!r} already exists in database. Skipping...")
            return

        if await accounts.get_user_by_api_key(session, api_key):
            typer.echo(f"User with api_key {api_key!r} already exists in database. Skipping...")
            return

        user_create = UserCreateForTask(
            first_name=first_name,
            last_name=last_name,
            username=username,
            role=role,
            password=password,
            api_key=api_key,
            workspaces=[WorkspaceCreate(name=workspace_name) for workspace_name in workspace],
        )

        user = await User.create(
            session,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            username=user_create.username,
            role=user_create.role,
            password_hash=accounts.hash_password(user_create.password),
            api_key=user_create.api_key,
            workspaces=[await get_or_new_workspace(session, workspace.name) for workspace in user_create.workspaces],
        )

        typer.echo("User successfully created:")
        typer.echo(f"• first_name: {user.first_name!r}")
        if user.last_name:
            typer.echo(f"• last_name: {user.last_name!r}")
        typer.echo(f"• username: {user.username!r}")
        typer.echo(f"• role: {user.role.value!r}")
        typer.echo(f"• api_key: {user.api_key!r}")
        typer.echo(f"• workspaces: {[workspace.name for workspace in user.workspaces]!r}")


def create(
    first_name: str = typer.Option(default=None, help="First name as a string."),
    username: str = typer.Option(
        default=None,
        prompt=True,
        help="Username as a lowercase string without spaces allowing letters, numbers, dashes and underscores.",
    ),
    role: UserRole = typer.Option(
        prompt=True,
        default=UserRole.annotator.value,
        show_default=True,
        help="Role for the user.",
    ),
    password: str = typer.Option(
        default=None,
        prompt=True,
        confirmation_prompt=True,
        hide_input=True,
        callback=password_callback,
        help=f"Password as a string with a minimum length of {USER_PASSWORD_MIN_LENGTH} characters.",
    ),
    last_name: str = typer.Option(default=None, help="Last name as a string."),
    api_key: Optional[str] = typer.Option(
        default=None,
        callback=api_key_callback,
        help=f"API key as a string with a minimum length of {USER_API_KEY_MIN_LENGTH} characters. If not specified a secure random API key will be generated",
    ),
    workspace: List[str] = typer.Option(
        default=[], help="A workspace that the user will be a member of (can be used multiple times)."
    ),
):
    asyncio.run(_create(first_name, username, role, password, last_name, api_key, workspace))


if __name__ == "__main__":
    typer.run(create)
