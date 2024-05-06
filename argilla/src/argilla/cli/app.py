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

import warnings

from argilla.cli import (
    datasets_app,
    info_app,
    login_app,
    logout_app,
    training_app,
    users_app,
    whoami_app,
    workspaces_app,
)
from argilla.cli.typer_ext import ArgillaTyper
from argilla.utils.dependency import is_package_with_extras_installed

warnings.simplefilter("ignore", UserWarning)

app = ArgillaTyper(help="Argilla CLI", no_args_is_help=True)


@app.error_handler(PermissionError)
def handler_permission_error(e: PermissionError) -> None:
    import sys

    from rich.console import Console

    from argilla.cli.rich import get_argilla_themed_panel

    panel = get_argilla_themed_panel(
        "Logged in user doesn't have enough permissions to execute this command",
        title="Not enough permissions",
        title_align="left",
        success=False,
    )

    Console().print(panel)
    sys.exit(1)


app.add_typer(datasets_app, name="datasets")
app.add_typer(info_app, name="info")
app.add_typer(login_app, name="login")
app.add_typer(logout_app, name="logout")
app.add_typer(training_app, name="train")
app.add_typer(users_app, name="users")
app.add_typer(whoami_app, name="whoami")
app.add_typer(workspaces_app, name="workspaces")

if is_package_with_extras_installed("argilla", ["server"]):
    from argilla_server.cli import app as server_app

    app.add_typer(server_app, name="server")

if __name__ == "__main__":
    app()
