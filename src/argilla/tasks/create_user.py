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
from pydantic import BaseModel, constr

from argilla.server.contexts.accounts import CRYPT_CONTEXT
from argilla.server.database import SessionLocal
from argilla.server.models import User, UserRole
from argilla.server.security.model import (
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USER_USERNAME_REGEX,
)


class UserCreate(BaseModel):
    username: constr(regex=USER_USERNAME_REGEX, min_length=1)
    role: Optional[UserRole]
    password: constr(min_length=USER_PASSWORD_MIN_LENGTH, max_length=USER_PASSWORD_MAX_LENGTH)
    api_key: Optional[str]


@click.command()
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--role", type=click.Choice(UserRole, case_sensitive=False))
@click.option("--api-key")
def create_user(username: str, password: str, role: Optional[UserRole], api_key: Optional[str]):
    with SessionLocal() as session, session.begin():
        user_create = UserCreate(username=username, password=password, role=role)

        user = User(
            first_name="",
            username=user_create.username,
            role=user_create.role,
            password_hash=CRYPT_CONTEXT.hash(user_create.password),
            api_key=api_key,
        )

        session.add(user)
        session.flush()
        session.refresh(user)

        print(f"User created successfully!")
        print(f"\nUsername: {user.username!r}" f"\nRole: {user.role.value!r}" f"\nAPI-Key: {user.api_key!r}")
        print("\nPlease, save user credentials")


if __name__ == "__main__":
    create_user()
