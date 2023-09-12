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

from typing import List, Optional

import typer

from argilla.client.sdk.users.models import UserRole


def create_user(
    username: str = typer.Option(..., prompt=True, help="The username of the user to be created"),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True, help="The password of the user to be created"
    ),
    first_name: Optional[str] = typer.Option(None, help="The first name of the user to be created"),
    last_name: Optional[str] = typer.Option(None, help="The last name of the user to be created"),
    role: UserRole = typer.Option(UserRole.annotator, help="The role of the user to be created"),
    workspaces: Optional[List[str]] = typer.Option(
        None,
        "--workspace",
        help="A workspace name to which the user will be linked to. This option can be provided several times.",
    ),
) -> None:
    from rich.markdown import Markdown

    from argilla.cli.rich import echo_in_panel
    from argilla.client.users import User

    try:
        user = User.create(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            workspaces=workspaces,
        )
    except KeyError as e:
        echo_in_panel(
            f"User with name={username} already exists.",
            title="User already exists",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e
    except ValueError as e:
        echo_in_panel(
            f"Provided parameters are not valid:\n\n{e}", title="Invalid parameters", title_align="left", success=False
        )
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        echo_in_panel(
            "An unexpected error occurred when trying to create the user.",
            title="Unexpected error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    workspaces_str = ", ".join(workspace.name for workspace in user.workspaces)

    echo_in_panel(
        Markdown(
            f"- **Username**: {user.username}\n"
            f"- **Role**: {user.role}\n"
            f"- **First name**: {user.first_name}\n"
            f"- **Last name**: {user.last_name}\n"
            f"- **API Key**: {user.api_key}\n"
            f"- **Workspaces**: {workspaces_str}"
        ),
        title="User created",
        title_align="left",
    )
