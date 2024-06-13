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

from typing import Optional

import typer

from argilla_v1.cli.callback import init_callback
from argilla_v1.cli.datasets.delete import delete_dataset
from argilla_v1.cli.datasets.list import list_datasets
from argilla_v1.cli.datasets.push import push_to_huggingface

_COMMANDS_REQUIRING_DATASET = ["delete", "push-to-huggingface"]


def callback(
    ctx: typer.Context,
    name: Optional[str] = typer.Option(None, help="The name of the `FeedbackDataset` to which apply the command"),
    workspace: Optional[str] = typer.Option(None, help="The name of the workspace where the `FeedbackDataset` belongs"),
) -> None:
    init_callback()

    from argilla_v1.cli.rich import echo_in_panel
    from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset

    if ctx.invoked_subcommand not in _COMMANDS_REQUIRING_DATASET:
        return

    if name is None:
        raise typer.BadParameter("The command requires a workspace name provided using '--name' option")

    try:
        dataset = FeedbackDataset.from_argilla(name=name, workspace=workspace)
    except ValueError as e:
        echo_in_panel(
            f"`FeedbackDataset` with name={name} not found in Argilla. Try using '--workspace' option."
            if not workspace
            else f"`FeedbackDataset with name={name} and workspace={workspace} not found in Argilla.",
            title="Dataset not found",
            title_align="left",
            success=False,
        )
        raise typer.Exit(1) from e
    except Exception as e:
        echo_in_panel(
            "An unexpected error occurred when trying to get the `FeedbackDataset` from Argilla.",
            title="Unexpected error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    ctx.obj = dataset


app = typer.Typer(help="Commands for dataset management", no_args_is_help=True, callback=callback)

app.command(name="list", help="List datasets linked to user's workspaces")(list_datasets)
app.command(name="push-to-huggingface", help="Push a dataset to HuggingFace Hub")(push_to_huggingface)
app.command(name="delete", help="Deletes a dataset")(delete_dataset)


if __name__ == "__main__":
    app()
