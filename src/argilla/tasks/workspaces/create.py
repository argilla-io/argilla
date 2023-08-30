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
from argilla.tasks import async_typer


def create_workspace(
    workspace_name: str,
):
    """Creates a workspace for the logged user in Argilla"""
    if not workspace_name:
        raise typer.BadParameter("Workspace name must be specified.")
    try:
        Workspace.create(name=workspace_name)
        typer.echo(f"Workspace with the name=`{workspace_name}` successfully created.")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    async_typer.run(create_workspace)
