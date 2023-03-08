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

import click

from argilla._constants import DEFAULT_API_KEY, DEFAULT_PASSWORD, DEFAULT_USERNAME
from argilla.server.contexts import accounts
from argilla.server.database import SessionLocal
from argilla.server.models import User, UserRole, Workspace


@click.command()
@click.option("-q", "--quiet", is_flag=True, default=False, help="Run without output.")
def create_default(quiet: bool):
    """Creates a user with default credentials on database suitable to start experimenting with argilla."""
    with SessionLocal() as session, session.begin():
        session.add(
            User(
                first_name="",
                username=DEFAULT_USERNAME,
                role=UserRole.admin,
                api_key=DEFAULT_API_KEY,
                password_hash=accounts.hash_password(DEFAULT_PASSWORD),
                workspaces=[Workspace(name=DEFAULT_USERNAME)],
            )
        )

    if not quiet:
        click.echo("User with default credentials succesfully created:")
        click.echo(f"• username: {DEFAULT_USERNAME!r}")
        click.echo(f"• password: {DEFAULT_PASSWORD!r}")
        click.echo(f"• api_key:  {DEFAULT_API_KEY!r}")


if __name__ == "__main__":
    create_default()
