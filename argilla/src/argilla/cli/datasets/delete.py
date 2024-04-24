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

from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset


def delete_dataset(ctx: typer.Context) -> None:
    from argilla.cli.rich import echo_in_panel

    dataset: "RemoteFeedbackDataset" = ctx.obj

    try:
        dataset.delete()
    except RuntimeError as e:
        echo_in_panel(
            "An unexpected error occurred when trying to delete the `FeedbackDataset`",
            title="Unexpected error",
            title_align="left",
            success=False,
        )
        raise typer.Exit(code=1) from e

    echo_in_panel(
        f"`FeedbackDataset` with name={dataset.name} and workspace={dataset.workspace.name} deleted successfully",
        title="Dataset deleted",
        title_align="left",
    )
