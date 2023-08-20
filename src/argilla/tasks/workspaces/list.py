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

from typing import List
from rich.console import Console
from rich.table import Table
import typer
from argilla import Workspace
from argilla.tasks import async_typer
from argilla.client import login


def list_workspaces(
    api_url: str = typer.Option(default="", help="The URL of the Argilla server."),
    api_key: str = typer.Option(default="", help="The API key to use when communicating with the Argilla server."),
) -> None:
    """List the workspaces in Argilla and prints them on the console."""
    if api_url == "" and api_key == "":
        # If the credentials are not provided, try to load them from the file.
        try:
            credentials = login.ArgillaCredentials.load()
            api_url = credentials.api_url
            api_key = credentials.api_key
        except FileNotFoundError:
            raise FileNotFoundError("The credentials file doesn't exist yet, you must pass your credentials.")

    login.login(api_url, api_key)

    workspaces = Workspace.list()
    table = Table(title="Workspaces")

    columns = ("ID", "Name", "Creation Date", "Update Date")
    [table.add_column(col, justify="center") for col in columns]

    def grab_fields(workspace: Workspace) -> List[str]:
        return [
            str(workspace.id),
            workspace.name,
            workspace.inserted_at.isoformat(sep=" "),
            workspace.updated_at.isoformat(sep=" "),
        ]

    for ws in workspaces:
        table.add_row(*grab_fields(ws))

    console = Console()
    console.print(table)


if __name__ == "__main__":
    async_typer.run(list_workspaces)
