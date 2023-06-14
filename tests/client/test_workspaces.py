#  coding=utf-8
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

import pytest
from argilla.client import api
from argilla.client.workspaces import Workspace

from tests.helpers import SecuredClient


def test_workspace_from_name(mocked_client: SecuredClient) -> None:
    the_api = api.active_api()
    workspace = the_api.http_client.post("/api/workspaces", json={"name": "test_workspace"})
    assert workspace["name"] == "test_workspace"

    api.init(api_key="argilla.apikey")
    with pytest.warns(DeprecationWarning):
        workspace = Workspace.from_name("test_workspace")
        assert workspace.name == "test_workspace"
        assert isinstance(workspace.id, str)


def test_workspace_init(mocked_client: SecuredClient) -> None:
    the_api = api.active_api()
    workspace = the_api.http_client.post("/api/workspaces", json={"name": "test_workspace"})
    assert workspace["name"] == "test_workspace"

    api.init(api_key="argilla.apikey")
    workspace = Workspace("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, str)


def test_workspace_init_errors(mocked_client: SecuredClient) -> None:
    api.init(api_key="argilla.apikey")

    with pytest.raises(ValueError, match="At least one of `name` or `id` must be provided."):
        Workspace()

    with pytest.raises(ValueError, match="Just one of `name` or `id` must be provided."):
        Workspace(name="name", id="id")

    with pytest.raises(ValueError, match="Workspace with name="):
        Workspace("non-existing-workspace")

    with pytest.raises(ValueError, match="The ID you provided is not a valid UUID"):
        Workspace(id="non-valid-uuid")

    with pytest.raises(ValueError, match="Workspace with id="):
        Workspace(id="00000000-0000-0000-0000-000000000000")


def test_workspace_create(mocked_client: SecuredClient) -> None:
    api.init(api_key="argilla.apikey")
    workspace = Workspace.create("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, str)

    the_api = api.active_api()
    workspaces = the_api.http_client.get("/api/workspaces")
    assert any(ws["name"] == "test_workspace" for ws in workspaces)


def test_workspace_add_user(mocked_client: SecuredClient) -> None:
    the_api = api.active_api()
    workspace = the_api.http_client.post("/api/workspaces", json={"name": "test_workspace"})
    assert workspace["name"] == "test_workspace"

    user = the_api.http_client.post(
        "/api/users",
        json={
            "first_name": "string",
            "last_name": "string",
            "username": "test_user",
            "role": "admin",
            "password": "stringst",
        },
    )
    assert user["username"] == "test_user"
    assert isinstance(user["id"], str)

    api.init(api_key="argilla.apikey")
    workspace = Workspace("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, str)
    workspace.add_user(user["id"])
    assert any(user.username == "test_user" for user in workspace.users)

    with pytest.raises(ValueError, match="User with id="):
        workspace.add_user(user["id"])

    workspace = Workspace("test_workspace")
    assert isinstance(workspace.users, list)
    assert any(user.username == "test_user" for user in workspace.users)


def test_workspace_delete_user(mocked_client: SecuredClient) -> None:
    the_api = api.active_api()
    workspace = the_api.http_client.post("/api/workspaces", json={"name": "test_workspace"})
    assert workspace["name"] == "test_workspace"

    user = the_api.http_client.post(
        "/api/users",
        json={
            "first_name": "string",
            "last_name": "string",
            "username": "test_user",
            "role": "admin",
            "password": "stringst",
        },
    )
    assert user["username"] == "test_user"
    assert isinstance(user["id"], str)

    added_user = the_api.http_client.post(f"/api/workspaces/{workspace['id']}/users/{user['id']}")
    assert added_user["workspaces"] == ["test_workspace"]

    api.init(api_key="argilla.apikey")
    workspace = Workspace("test_workspace")
    assert any("test_user" == user.username for user in workspace.users)
    workspace.delete_user(user["id"])
    assert not any(user.username == "test_user" for user in workspace.users)

    with pytest.raises(ValueError, match="Either the user with id="):
        workspace.delete_user(user["id"])
