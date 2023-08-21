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

from argilla.client.login import login as login_func

app = typer.Typer(invoke_without_command=True)


@app.callback(help="Login to an Argilla server")
def login(
    api_url: str = typer.Option(..., help="The URL of the Argilla server to login"),
    api_key: str = typer.Option(..., help="The API key to use to login to the Argilla server", prompt="API Key"),
    workspace: Optional[str] = typer.Option(
        None, help="The default workspace over which the operations will be performed"
    ),
):
    try:
        login_func(api_url=api_url, api_key=api_key, workspace=workspace, extra_headers={})
        typer.echo(f"Logged in successfully to '{api_url}' Argilla server!")
    except ValueError:
        typer.echo(
            f"Could not login to the '{api_url}' Argilla server. Please check the provided credentials and try again."
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
