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

app = typer.Typer(invoke_without_command=True)


@app.callback(help="Logout from an Argilla Server")
def logout(
    api_url: str = typer.Option(..., help="The URL of the Argilla Server to logout from"),
    api_key: str = typer.Option(..., help="The API key for logging out from the Argilla Server", prompt="API Key"),
    workspace: Optional[str] = typer.Option(
        None, help="The default workspace over which the operations will be performed"
    ),
    extra_headers: Optional[str] = typer.Option(
        None, help="A JSON string with extra headers to be sent in the requests to the Argilla Server"
    ),
):
    import json

    from argilla.client.logout import logout as logout_func

    try:
        if extra_headers:
            headers = json.loads(extra_headers)
        else:
            headers = {}
        logout_func(api_url=api_url, api_key=api_key, workspace=workspace, extra_headers=headers)
        typer.echo(f"Logged out successfully from '{api_url}' Argilla server!")
    except json.JSONDecodeError as e:
        typer.echo("The provided extra headers are not a valid JSON string.")
        raise typer.Exit(code=1) from e
    except ValueError as e:
        typer.echo(
            f"Could not logout from the '{api_url}' Argilla server. Please check the provided credentials and try again."
        )
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
