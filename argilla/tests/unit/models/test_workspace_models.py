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

from datetime import datetime

from dateutil import tz

from argilla._models import WorkspaceModel


class TestWorkspaceModels:
    def test_create_workspace_with_isoformat_string(self):
        workspace = WorkspaceModel(
            name="workspace",
            inserted_at="2024-12-12T09:44:24.989000Z",
            updated_at="2024-12-12T09:44:24.989000Z",
        )

        expected_datetime = datetime(2024, 12, 12, 9, 44, 24, 989000, tzinfo=tz.tzutc())

        assert workspace.name == "workspace"

        assert workspace.inserted_at == expected_datetime
        assert workspace.updated_at == expected_datetime
