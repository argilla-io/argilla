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

app = typer.Typer(invoke_without_command=True)


@app.callback(help="Check the current user on the Argilla Server")
def whoami() -> None:
    from rich.console import Console
    from rich.markdown import Markdown

    from argilla.client.api import active_client
    from argilla.tasks.callback import init_callback
    from argilla.tasks.rich import get_argilla_themed_panel

    init_callback()
    user = active_client()._user

    panel = get_argilla_themed_panel(
        Markdown(
            f"- **Username**: {user.username}\n"
            f"- **First name**: {user.first_name}\n"
            f"- **Last name**: {user.last_name}\n"
            f"- **API Key**: {user.api_key}\n"
            f"- **Workspaces**: {user.workspaces}"
        ),
        title="Current User",
        title_align="left",
    )

    Console().print(panel)


if __name__ == "__main__":
    app()
