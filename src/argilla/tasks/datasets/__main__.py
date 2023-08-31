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

from argilla.tasks.callback import init_callback
from argilla.tasks.datasets.list import list_datasets
from argilla.tasks.datasets.push import push_to_hf

app = typer.Typer(
    help="Holds CLI commands for datasets management", invoke_without_command=True, callback=init_callback
)

app.command(name="list", help="List datasets linked to user's workspaces")(list_datasets)
app.command(name="push-to-hf", help="Push a dataset to HuggingFace Hub")(push_to_hf)


if __name__ == "__main__":
    app()
