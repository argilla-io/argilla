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

from argilla import Argilla, Workspace


class TestWorkspacesManagement:
    def test_create_workspace(self, client: Argilla):
        workspace = Workspace(name="test_workspace")
        client.workspaces.add(workspace)

        assert workspace in client.workspaces
        assert workspace.exists()

    def test_create_and_delete_workspace(self, client: Argilla):
        workspace = client.workspaces(name="test_workspace")
        if workspace.exists():
            for dataset in workspace.datasets:
                dataset.delete()
            workspace.delete()

        workspace.create()
        assert workspace.exists()

        workspace.delete()
        assert not workspace.exists()

    def test_add_and_remove_users_to_workspace(self, client: Argilla):
        workspace = client.workspaces(name="test_workspace")

        test_user = client.users(username="test_user")
        if test_user.exists():
            test_user.delete()

        workspace.create()

        test_user.password = "test_password"
        test_user.create()

        user = workspace.add_user(user=test_user.username)
        assert user in workspace.users

        user = workspace.remove_user(user=user)
        assert user not in workspace.users
