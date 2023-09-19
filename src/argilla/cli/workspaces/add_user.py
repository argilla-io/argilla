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
    from argilla.cli.rich import echo_in_panel
    from argilla.cli.workspaces.utils import get_user
    from argilla.client.users import User

    workspace: "Workspace" = ctx.obj

    user = get_user(username)

    if user.is_owner:
        echo_in_panel(
            f"User with name={username} is an owner. Users with owner role don't need specific permissions per"
            " workspace, as those are super-users with privileges over everything under Argilla.",
            title="User is owner",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1)

    try:
        workspace.add_user(user.id)
    except ValueError as e:
        echo_in_panel(
            f"User with username={username} already exists in workspace={workspace.name}.",
            title="User already exists",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        echo_in_panel(
            "An unexpected error occurred when trying to add user to the workspace.",
            title="Unexpected error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    echo_in_panel(
        f"User with username={username} has been added to workspace={workspace.name}",
        title="User added",
        title_align="left",
    )
