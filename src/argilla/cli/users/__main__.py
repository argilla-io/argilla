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

import typer

from argilla.cli.callback import init_callback

from .create import create_user
from .delete import delete_user
from .list import list_users

app = typer.Typer(help="Commands for user management", no_args_is_help=True, callback=init_callback)
_COMMANDS_REQUIRING_USER = ["delete"]


def callback(
    ctx: typer.Context,
    username: Optional[str] = typer.Option(None, help="Username of the user to which apply the command."),
) -> None:
    init_callback()

    if ctx.invoked_subcommand not in _COMMANDS_REQUIRING_USER:
        return

    if username is None:
        raise typer.BadParameter("The command requires a username provided using '--username' option")

    from argilla.cli.rich import echo_in_panel
    from argilla.client.users import User

    try:
        user = User.from_name(username)
    except ValueError as e:
        echo_in_panel(
            f"User with username={username} doesn't exist.", title="User not found", title_align="left", success=False
        )
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        echo_in_panel(
            "An unexpected error occurred when trying to get the user.",
            title="Unexpected error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    ctx.obj = user


app = typer.Typer(help="Holds CLI commands for user management.", no_args_is_help=True, callback=callback)

app.command(name="create", help="Creates a new user")(create_user)
app.command(name="delete", help="Deletes a user")(delete_user)
app.command(name="list", help="List users")(list_users)
