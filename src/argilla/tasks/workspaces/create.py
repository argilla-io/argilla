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
        default=None,
        help="The name of the workspace to be created",
    )
) -> None:
    """Creates a workspace for the logged user in Argilla"""
    if not name:
        raise typer.BadParameter("Workspace name must be specified.")
    try:
        Workspace.create(name=name)
        typer.echo(f"Workspace with the name=`{name}` successfully created.")
    except ValueError as e:
        typer.echo(e)
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        typer.echo("An unexpected error occurred when trying to create the workspace")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    typer.run(create_workspace)
