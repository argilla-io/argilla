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


def push_to_huggingface(
    ctx: typer.Context,
    repo_id: str = typer.Option(..., help="The HuggingFace Hub repo where the dataset will be pushed to"),
    private: bool = typer.Option(False, help="Whether the dataset should be private or not"),
    token: Optional[str] = typer.Option(None, help="The HuggingFace Hub token to be used for pushing the dataset"),
) -> None:
    """Pushes a dataset from Argilla into the HuggingFace Hub. Note that this command
    is just available for `FeedbackDataset` datasets."""
    from rich.live import Live
    from rich.spinner import Spinner

    from argilla.cli.rich import echo_in_panel
    from argilla.client.feedback.dataset.local.dataset import FeedbackDataset

    dataset: "FeedbackDataset" = ctx.obj

    spinner = Spinner(
        name="dots",
        text=f"Pushing `FeedbackDataset` with name={dataset.name} and workspace={dataset.workspace.name} to the"
        " HuggingFace Hub...",
        style="red",
    )

    try:
        with Live(spinner, refresh_per_second=20):
            dataset.push_to_huggingface(repo_id=repo_id, private=private, token=token)
    except ValueError as e:
        echo_in_panel(
            "The `FeedbackDataset` has no records to push to the HuggingFace Hub. Make sure to add records before"
            " pushing it.",
            title="No records to push",
            title_align="left",
            success=False,
        )
        raise typer.Exit(1) from e
    except Exception as e:
        echo_in_panel(
            "An unexpected error occurred when trying to push the `FeedbackDataset` to the HuggingFace Hub",
            title="Unexpected error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    echo_in_panel(
        f"`FeedbackDataset` successfully pushed to the HuggingFace Hub at https://huggingface.co/{repo_id}",
        title="Dataset pushed",
        title_align="left",
    )
