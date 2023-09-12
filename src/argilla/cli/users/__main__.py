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

from argilla.cli.callback import init_callback

from .create import create_user
from .delete import delete_user
from .list import list_users

app = typer.Typer(help="Commands for user management", no_args_is_help=True, callback=init_callback)

app.command(name="create", help="Creates a new user")(create_user)
app.command(name="delete", help="Deletes a user")(delete_user)
app.command(name="list", help="List users")(list_users)
