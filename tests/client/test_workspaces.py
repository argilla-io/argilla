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
from uuid import UUID

import pytest
from argilla.client.api import ArgillaSingleton
from argilla.client.workspaces import Workspace

if TYPE_CHECKING:
    from argilla.server.models import User as ServerUser

from tests.factories import WorkspaceFactory, WorkspaceUserFactory


def test_workspace_cls_init() -> None:
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


def test_workspace_from_name(owner: "ServerUser"):
    workspace = WorkspaceFactory.create(name="test_workspace")
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)
    ArgillaSingleton.init(api_key=owner.api_key)

    found_workspace = Workspace.from_name(workspace.name)
    assert found_workspace.name == workspace.name
    assert isinstance(found_workspace.id, UUID)

    with pytest.raises(ValueError, match="Workspace with name="):
        Workspace.from_name("non-existing-workspace")


def test_workspace_from_id(owner: "ServerUser"):
    workspace = WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    found_workspace = Workspace.from_id(workspace.id)
    assert found_workspace.name == "test_workspace"
    assert isinstance(found_workspace.id, UUID)

    with pytest.raises(ValueError, match="The ID you provided is not a valid UUID"):
        Workspace.from_id(id="non-valid-uuid")

    with pytest.raises(ValueError, match="Workspace with id="):
        Workspace.from_id(id="00000000-0000-0000-0000-000000000000")


def test_workspace_create(owner: "ServerUser") -> None:
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.create(name="test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    with pytest.raises(ValueError, match="Workspace with name=`test_workspace` already exists"):
        Workspace.create("test_workspace")

    api = ArgillaSingleton.get()
    workspaces = api.http_client.get("/api/workspaces")
    assert any(ws["name"] == "test_workspace" for ws in workspaces)


def test_workspace_list(owner: "ServerUser") -> None:
    WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    workspaces = Workspace.list()
    assert any(ws.name == "test_workspace" for ws in workspaces)


def test_workspace_add_user(owner: "ServerUser") -> None:
    workspace = WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    workspace.add_user(owner.id)
    assert any(user.username == owner.username for user in workspace.users)

    with pytest.raises(ValueError, match="User with id="):
        workspace.add_user(owner.id)

    workspace = Workspace.from_name("test_workspace")
    assert isinstance(workspace.users, list)
    assert any(user.username == owner.username for user in workspace.users)


def test_workspace_delete_user(owner: "ServerUser") -> None:
    workspace = WorkspaceFactory.create(name="test_workspace")
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert any(user.username == "owner" for user in workspace.users)

    workspace.delete_user(owner.id)
    assert not any(user.username == owner.username for user in workspace.users)

    with pytest.raises(ValueError, match="Either the user with id="):
        workspace.delete_user(owner.id)
