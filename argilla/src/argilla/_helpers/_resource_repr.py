# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Dict

from huggingface_hub.utils import is_google_colab, is_notebook

RESOURCE_REPR_CONFIG = {
    "Dataset": {
        "columns": ["name", "id", "workspace_id", "updated_at"],
        "table_name": "Datasets",
        # "len_column": "records",
    },
    "Workspace": {
        "columns": ["name", "id", "updated_at"],
        "table_name": "Workspaces",
        # "len_column": "datasets",
    },
    "User": {"columns": ["username", "id", "role", "updated_at"], "table_name": "Users"},
    "Webhook": {"columns": ["url", "id", "events", "enabled", "updated_at"], "table_name": "Webhooks"},
}


class ResourceHTMLReprMixin:
    def _resource_to_table_row(self, resource) -> Dict[str, Any]:
        row = {}
        dumped_resource_model = resource.api_model().model_dump()
        resource_name = resource.__class__.__name__
        config = RESOURCE_REPR_CONFIG[resource_name].copy()
        len_column = config.pop("len_column", None)
        columns = config["columns"]
        if len_column is not None:
            row[len_column] = len(resource)
            columns = [column for column in columns if column != len_column]

        for column in columns:
            row[column] = dumped_resource_model[column]

        return row

    def _resource_to_table_name(self, resource) -> str:
        resource_name = resource.__class__.__name__
        return RESOURCE_REPR_CONFIG[resource_name]["table_name"]

    def _represent_as_html(self, resources) -> str:
        table_name = self._resource_to_table_name(resources[0])
        table_rows = [self._resource_to_table_row(resource) for resource in resources]

        html_table = f"<h3>{table_name}</h3><table><tr>"
        for column in table_rows[0]:
            html_table += f"<th>{column}</th>"
        html_table += "</tr>"

        for row in table_rows:
            html_table += "<tr>"
            for column in row:
                html_table += f"<td>{row[column]}</td>"
            html_table += "</tr>"

        html_table += "</table>"
        return html_table


class NotebookHTMLReprMixin:
    def __repr__(self) -> str:
        """Display the Argilla space in a notebook or Google Colab."""

        if is_notebook() or is_google_colab():
            from IPython.display import IFrame, display

            display(IFrame(src=self.api_url, frameborder=0, width=850, height=600))
            return f"Argilla has been deployed at: {self.api_url}"
        else:
            return super().__repr__()
