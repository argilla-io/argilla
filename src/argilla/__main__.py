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


import typer

from .tasks import database, server, training, users

app = typer.Typer(rich_help_panel=True, help="Argilla CLI", no_args_is_help=True)

app.add_typer(users, name="users")
app.add_typer(database, name="database")
app.add_typer(training, name="train")
app.add_typer(server, name="server")

if __name__ == "__main__":
    app()
