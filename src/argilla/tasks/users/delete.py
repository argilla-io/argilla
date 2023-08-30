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


def delete_user(username: str = typer.Argument(..., help="The username of the user to be removed")) -> None:
    from rich.console import Console

    from argilla.client.users import User
    from argilla.tasks.rich import get_argilla_themed_panel

    try:
        User.from_name(username).delete()
    except ValueError as e:
        typer.echo(f"User with username '{username}' doesn't exist!")
        raise typer.Exit(code=1) from e
    except RuntimeError as e:
        typer.echo("An unexpected error occurred when trying to remove the user")
        raise typer.Exit(code=1) from e

    panel = get_argilla_themed_panel(
        f"User with username '{username}' has been removed!", title="User removed", title_align="left"
    )
    Console().print(panel)
