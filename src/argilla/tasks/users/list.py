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


def list_users() -> None:
    from rich.console import Console

    from argilla.client.users import User
    from argilla.tasks.rich import get_argilla_themed_table

    try:
        users = User.list()
    except RuntimeError as e:
        typer.echo("An unexpected error occurred when trying to retrieve the list of users from the Argilla server")
        raise typer.Exit(code=1) from e

    table = get_argilla_themed_table(title="Users")
    for column in ("ID", "Username", "Role", "First name", "Last name", "Creation Date", "Last Updated Date"):
        table.add_column(column)

    for user in users:
        table.add_row(
            str(user.id),
            user.username,
            user.role,
            user.first_name,
            user.last_name,
            user.inserted_at.isoformat(sep=" "),
            user.updated_at.isoformat(sep=" "),
        )

    Console().print(table)
