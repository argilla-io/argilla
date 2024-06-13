#  coding=utf-8
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

from argilla_v1.cli.callback import init_callback

from .add_user import add_user
from .create import create_workspace
from .delete_user import delete_user
from .list import list_workspaces

_COMMANDS_REQUIRING_WORKSPACE = ["add-user", "delete-user"]


def callback(
    ctx: typer.Context,
    name: Optional[str] = typer.Option(None, help="Name of the workspace to which apply the command."),
) -> None:
    init_callback()

    if ctx.invoked_subcommand not in _COMMANDS_REQUIRING_WORKSPACE:
        return

    if name is None:
        raise typer.BadParameter("The command requires a workspace name provided using '--name' option")

    from argilla_v1.cli.rich import echo_in_panel
    from argilla_v1.client.workspaces import Workspace

    try:
        workspace = Workspace.from_name(name)
    except ValueError as e:
        echo_in_panel(
            f"Workspace with name={name} does not exist.",
            title="Workspace not found",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        echo_in_panel(
            "An unexpected error occurred when trying to get the workspace from the Argilla server",
            title="Unexpected error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    ctx.obj = workspace


app = typer.Typer(help="Commands for workspace management", no_args_is_help=True, callback=callback)

app.command(name="create", help="Create a workspace")(create_workspace)
app.command(name="list", help="Lists workspaces of the logged user.")(list_workspaces)
app.command(name="delete-user", help="Deletes a user from a workspace.")(delete_user)
app.command(name="add-user", help="Adds a user to a workspace.")(add_user)


if __name__ == "__main__":
    app()
