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

from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from argilla.client.workspaces import Workspace


def add_user(
    ctx: typer.Context,
    username: str = typer.Argument(..., help="The username of the user to be added to the workspace"),
) -> None:
    from rich.console import Console

    from argilla.client.users import User
    from argilla.tasks.rich import get_argilla_themed_panel

    workspace: "Workspace" = ctx.obj

    try:
        user = User.from_name(username)
    except ValueError as e:
        typer.echo(f"User with username '{username}' does not exist")
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        typer.echo("An unexpected error occurred when trying to retrieve the user from the Argilla server")
        raise typer.Exit(code=1) from e

    try:
        workspace.add_user(user.id)
    except ValueError as e:
        typer.echo(f"User with username '{username}' already exists in workspace '{workspace.name}'")
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        typer.echo("An unexpected error occurred when trying to add user to the workspace")
        raise typer.Exit(code=1) from e

    panel = get_argilla_themed_panel(
        f"User with username '{username}' has been added to '{workspace.name}' workspace",
        title="User Added",
        title_align="left",
    )
    Console().print(panel)
