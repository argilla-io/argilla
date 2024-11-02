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

import uuid

import argilla as rg
from argilla._helpers._resource_repr import ResourceHTMLReprMixin
from argilla._models import DatasetModel


class TestResourceHTMLReprMixin:
    def test_represent_workspaces_as_html(self):
        client = rg.Argilla()
        workspaces = [
            rg.Workspace(name="workspace1", id=uuid.uuid4()),
            rg.Workspace(name="workspace2", id=uuid.uuid4()),
        ]

        assert (
            ResourceHTMLReprMixin()._represent_as_html(workspaces) == "<h3>Workspaces</h3>"
            "<table>"
            "<tr><th>name</th><th>id</th><th>updated_at</th></tr>"
            f"<tr><td>workspace1</td><td>{str(workspaces[0].id)}</td><td>None</td></tr>"
            f"<tr><td>workspace2</td><td>{str(workspaces[1].id)}</td><td>None</td></tr>"
            "</table>"
            ""
        )

        workspace = rg.Workspace(name="workspace1", id=uuid.uuid4())
        datasets = [
            rg.Dataset(name="dataset1", workspace=workspace, client=client),
            rg.Dataset(name="dataset2", workspace=workspace, client=client),
        ]

        for dataset in datasets:
            dataset.id = uuid.uuid4()

        assert (
            ResourceHTMLReprMixin()._represent_as_html(datasets) == "<h3>Datasets</h3>"
            "<table>"
            "<tr><th>name</th><th>id</th><th>workspace_id</th><th>updated_at</th></tr>"
            f"<tr><td>dataset1</td><td>{str(datasets[0].id)}</td><td>{str(workspace.id)}</td><td>None</td></tr>"
            f"<tr><td>dataset2</td><td>{str(datasets[1].id)}</td><td>{str(workspace.id)}</td><td>None</td></tr>"
            "</table>"
        )
