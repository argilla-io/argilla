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

from .migrate import migrate_db
from .revisions import revisions
from .users import app as users_app

app = typer.Typer(help="Commands for Argilla server database management", no_args_is_help=True)

app.add_typer(users_app, name="users")
app.command(name="migrate", help="Run database migrations.")(migrate_db)
app.command(name="revisions", help="Show available revisions.")(revisions)

if __name__ == "__main__":
    app()
