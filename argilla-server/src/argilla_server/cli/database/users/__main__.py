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
from typer import Typer

from .create import create
from .create_default import create_default
from .migrate import migrate
from .update import update

app = Typer(help="Commands for user management using the database connection", no_args_is_help=True)

app.command(name="create_default", help="Creates default users and workspaces in the Argilla database.")(create_default)
app.command(name="create", help="Creates a user and add it to the Argilla database.", no_args_is_help=True)(create)
app.command(name="update", help="Updates the user's role into the Argilla database.", no_args_is_help=True)(update)
app.command(name="migrate")(migrate)


if __name__ == "__main__":
    app()
