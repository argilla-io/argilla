#  coding=utf-8
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

from argilla.tasks.async_typer import AsyncTyper
from argilla.tasks.callback import init_callback

from .create import create_workspace
from .list import list_workspaces

app = AsyncTyper(help="Holds CLI commands for workspace management.", no_args_is_help=True, callback=init_callback)

app.command(name="list", help="Lists workspaces of the logged user.")(list_workspaces)
app.command(name="create", help="Create a workspace for the logged user.")(create_workspace)


if __name__ == "__main__":
    app()
