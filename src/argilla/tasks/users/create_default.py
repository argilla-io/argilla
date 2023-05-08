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

import typer

from argilla._constants import DEFAULT_API_KEY, DEFAULT_PASSWORD, DEFAULT_USERNAME
from argilla.server.contexts import accounts
from argilla.server.database import SessionLocal
from argilla.server.models import User, UserRole, Workspace


def create_default(
    api_key: str = typer.Option(default=DEFAULT_API_KEY, help="API key for the user."),
    password: str = typer.Option(default=DEFAULT_PASSWORD, help="Password for the user."),
    quiet: bool = typer.Option(is_flag=True, default=False, help="Run without output."),
):
    """Creates a user with default credentials on database suitable to start experimenting with argilla."""
    with SessionLocal() as session:
        if accounts.get_user_by_username(session, DEFAULT_USERNAME):
            if not quiet:
                typer.echo("User with default username already found on database, will not do anything.")

            return

        session.add(
            User(
                first_name="",
                username=DEFAULT_USERNAME,
                role=UserRole.admin,
                api_key=api_key,
                password_hash=accounts.hash_password(password),
                workspaces=[Workspace(name=DEFAULT_USERNAME)],
            )
        )
        session.commit()

        if not quiet:
            typer.echo("User with default credentials succesfully created:")
            typer.echo(f"• username: {DEFAULT_USERNAME!r}")
            typer.echo(f"• password: {password!r}")
            typer.echo(f"• api_key:  {api_key!r}")


if __name__ == "__main__":
    typer.run(create_default)
