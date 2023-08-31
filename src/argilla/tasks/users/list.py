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

from typing import List, Optional, Union

import typer


def list_users(
    workspace: Optional[str] = typer.Option(None, help="Filter users by workspace"),
    role: Optional[str] = typer.Option(None, help="Filter users by role"),
) -> None:
    from rich.console import Console

    from argilla.client.sdk.v1.workspaces.models import WorkspaceModel
    from argilla.client.users import User
    from argilla.client.workspaces import Workspace
    from argilla.tasks.rich import get_argilla_themed_table

    def build_workspaces_text(workspaces: Union[List[str], List[WorkspaceModel], None]) -> str:
        text = ""
        if not workspaces:
            return text
        for i, workspace in enumerate(workspaces):
            workspace_name = workspace.name if isinstance(workspace, WorkspaceModel) else workspace
            text += f"• {workspace_name}"
            if i < len(workspaces) - 1:
                text += "\n"
        return text

    try:
        if workspace is not None:
            users = Workspace.from_name(workspace).users
        else:
            users = User.list()
    except ValueError as e:
        typer.echo(f"Workspace '{workspace}' does not exist!")
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        typer.echo("An unexpected error occurred when trying to retrieve the list of users from the Argilla server")
        raise typer.Exit(code=1) from e

    table = get_argilla_themed_table(title="Users", show_lines=True)
    for column in (
        "ID",
        "Username",
        "Role",
        "First name",
        "Last name",
        "Workspaces",
        "Creation Date",
        "Last Updated Date",
    ):
        table.add_column(column)

    for user in users:
        if role is not None and user.role != role:
            continue
        table.add_row(
            str(user.id),
            user.username,
            user.role,
            user.first_name,
            user.last_name,
            build_workspaces_text(user.workspaces),
            user.inserted_at.isoformat(sep=" "),
            user.updated_at.isoformat(sep=" "),
        )

    Console().print(table)
