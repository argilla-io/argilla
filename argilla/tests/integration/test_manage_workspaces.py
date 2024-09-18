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

from argilla import Argilla, Workspace, User


class TestWorkspacesManagement:
    def test_create_workspace(self, client: Argilla):
        workspace = Workspace(name=f"test_workspace{uuid.uuid4()}")
        client.workspaces.add(workspace)

        assert workspace in client.workspaces
        assert client.api.workspaces.exists(workspace.id)

    def test_create_and_delete_workspace(self, client: Argilla):
        workspace = client.workspaces(name="test_workspace")
        if workspace:
            for dataset in workspace.datasets:
                dataset.delete()
            workspace.delete()

        workspace = Workspace(name="test_workspace").create()
        assert client.api.workspaces.exists(workspace.id)

        workspace.delete()
        assert not client.api.workspaces.exists(workspace.id)

    def test_add_and_remove_users_to_workspace(self, client: Argilla, workspace: Workspace):
        ws_name = "test_workspace"
        username = "test_user"

        workspace = client.workspaces(name=ws_name)
        if workspace:
            for dataset in workspace.datasets:
                dataset.delete()
            workspace.delete()

        test_user = client.users(username=username)
        if test_user:
            test_user.delete()

        workspace = Workspace(name=ws_name).create()
        test_user = User(username=username, password="test_password").create()

        user = workspace.add_user(user=test_user.username)
        assert user in workspace.users

        user = workspace.remove_user(user=user)
        assert user not in workspace.users
