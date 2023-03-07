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
@click.option("--last-name")
@click.option("--username", prompt=True)
@click.option(
    "--role", prompt=True, type=click.Choice(UserRole.__members__, case_sensitive=False), default=UserRole.annotator
)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_user(username: str, password: str, role: Optional[UserRole], first_name: str, last_name: Optional[str]):
    with SessionLocal() as session:
        user_create = UserCreate(
            username=username, password=password, role=role, first_name=first_name, last_name=last_name
        )
        user = accounts.create_user(session, user_create)

        print(f"User created successfully!")
        print(_show_created_user(user))
        print("\nPlease, save user credentials")


if __name__ == "__main__":
    create_user()
