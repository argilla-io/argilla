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

from typing import List, Optional

import click
from pydantic import constr
from sqlalchemy.orm import Session

from argilla.server.contexts import accounts
from argilla.server.database import SessionLocal
from argilla.server.models import User, UserRole, Workspace
from argilla.server.security.model import (
    USER_PASSWORD_MIN_LENGTH,
    UserCreate,
    WorkspaceCreate,
)

USER_API_KEY_MIN_LENGTH = 8


class UserCreateForTask(UserCreate):
    api_key: Optional[constr(min_length=USER_API_KEY_MIN_LENGTH)]
    workspaces: Optional[List[WorkspaceCreate]]


def _get_or_new_workspace(session: Session, workspace_name: str):
    return session.query(Workspace).filter_by(name=workspace_name).first() or Workspace(name=workspace_name)


@click.command()
@click.option("--first-name", prompt=True)
@click.option("--last-name")
@click.option(
    "--username",
    prompt=True,
    help="Username as a lowercase string without spaces allowing letters, numbers, dashes and underscores.",
)
@click.option(
    "--role",
    prompt=True,
    type=click.Choice(UserRole.__members__, case_sensitive=False),
    default=UserRole.annotator,
    show_default=True,
    help="Role for the user.",
)
@click.password_option(
    "--password",
    prompt=f"Password (min. {USER_PASSWORD_MIN_LENGTH} characters)",
    help=f"Password as a string with a minimum length of {USER_PASSWORD_MIN_LENGTH} characters.",
)
@click.option(
    "--api-key",
    help=f"API key as a string with a minimum length of {USER_API_KEY_MIN_LENGTH} characters. If not specified a secure random API key will be generated",
)
@click.option(
    "--workspace", multiple=True, help="A workspace that the user will be a member of (can be used multiple times)."
)
def create(
    first_name: str,
    username: str,
    role: UserRole,
    password: str,
    last_name: Optional[str],
    api_key: Optional[str],
    workspace: Optional[List[str]],
):
    """Creates a new user in the Argilla database with provided parameters"""
    with SessionLocal() as session:
        if accounts.get_user_by_username(session, username):
            click.echo(f"User with username {username!r} already exists in database. Skipping...")
            return

        if accounts.get_user_by_api_key(session, api_key):
            click.echo(f"User with api_key {api_key!r} already exists in database. Skipping...")
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

        user = User(
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            username=user_create.username,
            role=user_create.role,
            password_hash=accounts.hash_password(user_create.password),
            api_key=user_create.api_key,
            workspaces=[_get_or_new_workspace(session, workspace.name) for workspace in user_create.workspaces],
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        click.echo("User successfully created:")
        click.echo(f"• first_name: {user.first_name!r}")
        if user.last_name:
            click.echo(f"• last_name: {user.last_name!r}")
        click.echo(f"• username: {user.username!r}")
        click.echo(f"• role: {user.role.value!r}")
        click.echo(f"• api_key: {user.api_key!r}")
        click.echo(f"• workspaces: {[workspace.name for workspace in user.workspaces]!r}")


if __name__ == "__main__":
    create()
