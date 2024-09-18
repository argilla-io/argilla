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

from typing import Dict, Optional

import typer

from argilla_v1.client.enums import DatasetType


def list_datasets(
    workspace: Optional[str] = typer.Option(None, help="Filter datasets by workspace"),
    type_: Optional[DatasetType] = typer.Option(
        None,
        "--type",
        help="The type of datasets to be listed. This option can be used multiple times. By default, all datasets are listed.",
    ),
) -> None:
    from rich.console import Console

    from argilla_v1.cli.rich import echo_in_panel, get_argilla_themed_table
    from argilla_v1.client.api import list_datasets as list_datasets_api
    from argilla_v1.client.sdk.datasets.models import Dataset
    from argilla_v1.client.workspaces import Workspace

    console = Console()

    def build_tags_text(tags: Dict[str, str]) -> str:
        text = ""
        for i, (tag, description) in enumerate(tags.items()):
            text += f"• [b]{tag}[not b]: {description}"
            if i < len(tags) - 1:
                text += "\n"
        return text

    table = get_argilla_themed_table(title="Datasets", show_lines=True)
    for column in ("ID", "Name", "Workspace", "Type", "Tags", "Creation Date", "Last Update Date"):
        table.add_column(column, justify="center" if column != "Tags" else "left")

    if workspace is not None:
        try:
            Workspace.from_name(workspace)
        except ValueError as e:
            echo_in_panel(
                f"Workspace with name={workspace} does not exist",
                title="Workspace not found",
                title_align="left",
                success=False,
            )
            raise typer.Exit(code=1) from e

    for dataset in list_datasets_api(workspace, type_):
        if isinstance(dataset, Dataset):
            table.add_row(
                dataset.id,
                dataset.name,
                dataset.workspace,
                dataset.task,
                build_tags_text(dataset.tags),
                dataset.created_at.isoformat(sep=" "),
                dataset.last_updated.isoformat(sep=" "),
            )
        else:
            table.add_row(
                str(dataset.id),
                dataset.name,
                dataset.workspace.name,
                "Feedback",
                None,
                dataset.created_at.isoformat(sep=" "),
                dataset.updated_at.isoformat(sep=" "),
            )

    console.print(table)
