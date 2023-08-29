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

from enum import Enum
from typing import Dict, Optional

import typer


class DatasetKind(str, Enum):
    feedback = "feedback"
    other = "other"


def list_datasets(
    workspace: Optional[str] = typer.Option(None, help="List datasets in this workspace"),
    kind: Optional[DatasetKind] = typer.Option(
        None,
        help="List datasets of this kind. This option can be used multiple times. By default, all datasets are listed.",
    ),
) -> None:
    from rich.console import Console
    from rich.markdown import Markdown

    from argilla.client.api import list_datasets as list_datasets_api
    from argilla.client.feedback.dataset.local import FeedbackDataset
    from argilla.tasks.rich import get_argilla_themed_table

    def build_tags_text(tags: Dict[str, str]) -> Markdown:
        text = ""
        for tag, description in tags.items():
            text += f"- **{tag}**: {description}\n"
        return Markdown(text)

    table = get_argilla_themed_table(title="Datasets")
    for column in ("ID", "Name", "Workspace", "Kind", "Tags", "Creation Date", "Update Date"):
        table.add_column(column, justify="center")

    if kind is None or kind == DatasetKind.feedback:
        for dataset in FeedbackDataset.list(workspace):
            # TODO: add passing value for `Creation Date` and `Update Date` columns once `RemoteFeedbackDataset` has
            # these attributes
            table.add_row(str(dataset.id), dataset.name, dataset.workspace.name, "Feedback", None, None, None)

    if kind is None or kind == DatasetKind.other:
        for dataset in list_datasets_api(workspace):
            table.add_row(
                dataset.id,
                dataset.name,
                dataset.workspace,
                dataset.task,
                build_tags_text(dataset.tags),
                dataset.created_at.isoformat(sep=" "),
                dataset.last_updated.isoformat(sep=" "),
            )

    console = Console()
    console.print(table)


if __name__ == "__main__":
    typer.run(list_datasets)
