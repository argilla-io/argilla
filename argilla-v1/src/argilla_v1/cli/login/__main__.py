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


@app.callback(help="Login to an Argilla Server")
def login(
    api_url: str = typer.Option(..., help="The URL of the Argilla Server to login in to"),
    api_key: str = typer.Option(
        ..., prompt="API Key", hide_input=True, help="The API key for logging into the Argilla Server"
    ),
    workspace: Optional[str] = typer.Option(
        None, help="The default workspace over which the operations will be performed"
    ),
    extra_headers: Optional[str] = typer.Option(
        None, help="A JSON string with extra headers to be sent in the requests to the Argilla Server"
    ),
):
    import json

    from argilla_v1.cli.rich import echo_in_panel
    from argilla_v1.client.login import login as login_func

    try:
        if extra_headers:
            headers = json.loads(extra_headers)
        else:
            headers = {}
        login_func(api_url=api_url, api_key=api_key, workspace=workspace, extra_headers=headers)
    except json.JSONDecodeError as e:
        echo_in_panel(
            "The provided extra headers are not a valid JSON string.",
            title="Extra headers error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e
    except ValueError as e:
        echo_in_panel(
            f"Could not login to the '{api_url}' Argilla server. Please check the provided credentials and try again.",
            title="Login error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    echo_in_panel(f"Logged in successfully to '{api_url}' Argilla server!", title="Logged in", title_align="left")


if __name__ == "__main__":
    app()
