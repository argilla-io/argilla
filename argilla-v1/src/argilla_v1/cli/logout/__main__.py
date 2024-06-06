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


@app.callback(help="Logout from an Argilla Server")
def logout(force: bool = typer.Option(False, help="Force the logout even if the server cannot be reached")) -> None:
    from argilla_v1.cli.callback import init_callback
    from argilla_v1.cli.rich import echo_in_panel
    from argilla_v1.client.login import ArgillaCredentials

    if not force:
        init_callback()

    ArgillaCredentials.remove()

    echo_in_panel("Logged out successfully from Argilla server!", title="Logout", title_align="left")


if __name__ == "__main__":
    app()
