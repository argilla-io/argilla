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


def push_to_hf(
    name: str = typer.Option(..., help="The name of the dataset to be pushed to the HuggingFace Hub"),
    workspace: Optional[str] = typer.Option(None, help="The name of the workspace where the dataset is located"),
    repo_id: str = typer.Option(..., help="The HuggingFace Hub repo where the dataset will be pushed to"),
    private: bool = typer.Option(False, help="Whether the dataset should be private or not"),
    token: Optional[str] = typer.Option(None, help="The HuggingFace Hub token to be used for pushing the dataset"),
) -> None:
    """Pushes a dataset from Argilla into the HuggingFace Hub. Note that this command
    is just available for `FeedbackDataset` datasets."""
    from rich.console import Console

    from argilla.client.feedback.dataset.local import FeedbackDataset

    console = Console()

    try:
        console.print(
            f":one: Retrieving `FeedbackDataset` with name={name} from Argilla..."
            if not workspace
            else f":one: Retrieving `FeedbackDataset` with name={name} and workspace={workspace} from Argilla..."
        )
        dataset = FeedbackDataset.from_argilla(name=name, workspace=workspace)
    except ValueError as e:
        typer.echo(
            f"`FeedbackDataset` with name={name} not found in Argilla."
            if not workspace
            else f"`FeedbackDataset with name={name} and workspace={workspace} not found in Argilla."
        )
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo("An unexpected error occurred when trying to get the `FeedbackDataset` from Argilla.")
        raise typer.Exit(code=1) from e

    try:
        console.print(
            f":two: Pushing `FeedbackDataset` with name={name} to the HuggingFace Hub..."
            if not workspace
            else f":two: Pushing `FeedbackDataset` with name={name} and workspace={workspace} to the HuggingFace Hub..."
        )
        dataset.push_to_huggingface(repo_id=repo_id, private=private, token=token)
        console.print(
            f":sparkles: `FeedbackDataset` successfully pushed to the :hugs: HuggingFace Hub at https://huggingface.co/{repo_id}"
        )
    except ValueError as e:
        typer.echo(
            f"The `FeedbackDataset` has no records to push to the HuggingFace Hub. Make"
            " sure to add records before pushing it."
        )
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo("An unexpected error occurred when trying to push the `FeedbackDataset` to the HuggingFace Hub")
        raise typer.Exit(code=1) from e
