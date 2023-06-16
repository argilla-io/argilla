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

from uuid import UUID

import pytest
from argilla.client import api
from argilla.client.workspaces import Workspace

from tests.factories import UserFactory, WorkspaceFactory, WorkspaceUserFactory
from tests.helpers import SecuredClient


def test_workspace_init() -> None:
    with pytest.raises(
        Exception,
        match=r"`Workspace` cannot be initialized via the `__init__` method | you should use `Workspace.from_name\('test_workspace'\)`",
    ):
        Workspace(name="test_workspace")

    with pytest.raises(
        Exception,
        match=r"`Workspace` cannot be initialized via the `__init__` method | you should use `Workspace.from_id\('00000000-0000-0000-0000-000000000000'\)`",
    ):
        Workspace(id="00000000-0000-0000-0000-000000000000")


def test_workspace_from_name(mocked_client: SecuredClient) -> None:
    WorkspaceFactory.create(name="test_workspace")

    api.init(api_key="argilla.apikey")
    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)


def test_workspace_from_name_errors(mocked_client: SecuredClient) -> None:
    api.init(api_key="argilla.apikey")

    with pytest.raises(ValueError, match="Workspace with name="):
        Workspace.from_name("non-existing-workspace")


def test_workspace_from_id_errors(mocked_client: SecuredClient) -> None:
    api.init(api_key="argilla.apikey")

    with pytest.raises(ValueError, match="The ID you provided is not a valid UUID"):
        Workspace.from_id(id="non-valid-uuid")

    with pytest.raises(ValueError, match="Workspace with id="):
        Workspace.from_id(id="00000000-0000-0000-0000-000000000000")


def test_workspace_create(mocked_client: SecuredClient) -> None:
    api.init(api_key="argilla.apikey")
    workspace = Workspace.create("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    the_api = api.active_api()
    workspaces = the_api.http_client.get("/api/workspaces")
    assert any(ws["name"] == "test_workspace" for ws in workspaces)


def test_workspace_add_user(mocked_client: SecuredClient) -> None:
    WorkspaceFactory.create(name="test_workspace")
    user = UserFactory.create(username="test_user")

    api.init(api_key="argilla.apikey")
    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)
    workspace.add_user(user.id)
    assert any(user.username == "test_user" for user in workspace.users)

    with pytest.raises(ValueError, match="User with id="):
        workspace.add_user(user.id)

    workspace = Workspace.from_name("test_workspace")
    assert isinstance(workspace.users, list)
    assert any(user.username == "test_user" for user in workspace.users)


def test_workspace_delete_user(mocked_client: SecuredClient) -> None:
    workspace = WorkspaceFactory.create(name="test_workspace")
    user = UserFactory.create(first_name="test", username="test_user", api_key="test_user.apikey")
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=user.id)

    api.init(api_key="argilla.apikey")
    workspace = Workspace.from_name("test_workspace")
    assert any("test_user" == user.username for user in workspace.users)
    workspace.delete_user(user.id)
    assert not any(user.username == "test_user" for user in workspace.users)

    with pytest.raises(ValueError, match="Either the user with id="):
        workspace.delete_user(user.id)


def test_workspace_list(mocked_client: SecuredClient) -> None:
    WorkspaceFactory.create(name="test_workspace")

    api.init(api_key="argilla.apikey")
    workspaces = Workspace.list()
    assert any(ws.name == "test_workspace" for ws in workspaces)
