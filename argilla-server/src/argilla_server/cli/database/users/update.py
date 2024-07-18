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

import typer

from argilla_server.contexts import accounts
from argilla_server.database import AsyncSessionLocal
from argilla_server.models import UserRole


async def _update(username: str, role: UserRole):
    async with AsyncSessionLocal() as session:
        user = await accounts.get_user_by_username(session, username)

        if not user:
            typer.echo(f"User with username {username!r} does not exists in database. Skipping...")
            return

        if user.role == role:
            typer.echo(f"User {username!r} already has role {role.value!r}. Skipping...")
            return

        old_role = user.role

        user = await user.update(session, role=role)

        typer.echo(f"User {username!r} successfully updated:")
        typer.echo(f"• role: {old_role.value!r} -> {user.role.value!r}")


def update(
    username: str = typer.Argument(
        default=None,
        help="Username as a lowercase string without spaces allowing letters, numbers, dashes and underscores.",
    ),
    role: UserRole = typer.Option(
        prompt=True,
        default=None,
        show_default=False,
        help="New role for the user.",
    ),
):
    asyncio.run(_update(username, role))


if __name__ == "__main__":
    typer.run(update)
