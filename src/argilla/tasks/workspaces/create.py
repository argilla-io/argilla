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

from argilla.client.workspaces import Workspace


def create_workspace(
    name: str = typer.Argument(
        ...,
        help="The name of the workspace to be created",
    )
) -> None:
    """Creates a workspace for the logged user in Argilla"""
    from rich.console import Console
    from argilla.tasks.rich import get_argilla_themed_panel
    try:
        Workspace.create(name=name)
        panel = get_argilla_themed_panel(
            f"Workspace with the name=`{name}` successfully created.", title="Workspace created", title_align="left"
        )
        Console().print(panel)
    except ValueError as e:
        typer.echo(e)
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        typer.echo(
            "An unexpected error occurred when trying to create the workspace")
        raise typer.Exit(code=1) from e
