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

from typing import Optional

import click

from argilla.server.contexts import accounts
from argilla.server.database import SessionLocal
from argilla.server.models import User, UserRole
from argilla.server.security.model import UserCreate


def _show_created_user(user: User):
    message = f"\nUsername: {user.username!r}" f"\nRole: {user.role.value!r}" f"\nFirst name: {user.first_name!r}"

    if user.last_name:
        message += f"\nLast name: {user.last_name!r}"

    message += f"\nAPI-Key: {user.api_key!r}"

    return message


@click.command()
@click.option("--first-name", prompt=True)
@click.option("--username", prompt=True)
@click.option(
    "--role",
    prompt=True,
    type=click.Choice(UserRole.__members__, case_sensitive=False),
    default=UserRole.annotator,
    show_default=True,
)
@click.password_option("--password", prompt=True)
@click.option("--last-name", required=False)
def create_user(first_name: str, username: str, role: UserRole, password: str, last_name: Optional[str]):
    """Creates a new user in the Argilla DB with provided parameters"""

    with SessionLocal() as session:
        user_create = UserCreate(
            username=username, password=password, role=role, first_name=first_name, last_name=last_name
        )
        user = accounts.create_user(session, user_create)

        click.echo(f"User created successfully!")
        click.echo(_show_created_user(user))
        click.echo("\nPlease, save user credentials")


if __name__ == "__main__":
    create_user()
