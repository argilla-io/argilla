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

from argilla.cli.rich import echo_in_panel
from argilla.client.login import ArgillaCredentials
from argilla.client.singleton import init


def init_callback() -> None:
    if not ArgillaCredentials.exists():
        echo_in_panel(
            "You are not logged in. Please run 'argilla login' to login to an Argilla server.",
            title="Not logged in",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1)

    try:
        init()
    except Exception as e:
        echo_in_panel(
            "The Argilla Server you are logged in is not available or not responding. Please make sure it's running and try again.",
            title="Server not available",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e


def deprecated_database_cmd_callback(ctx: typer.Context) -> None:
    echo_in_panel(
        f"Instead you should run `argilla server database {ctx.invoked_subcommand}`",
        title="Deprecated command",
        title_align="left",
        success=False,
    )
