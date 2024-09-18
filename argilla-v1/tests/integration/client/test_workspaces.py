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
from uuid import UUID, uuid4

import pytest
from argilla_v1.client.sdk.users.models import UserModel, UserRole
from argilla_v1.client.singleton import ArgillaSingleton
from argilla_v1.client.workspaces import Workspace

from tests.factories import (
    DatasetFactory,
    UserFactory,
    WorkspaceFactory,
    WorkspaceUserFactory,
)

if TYPE_CHECKING:
    from argilla_server.models import User as ServerUser


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


@pytest.mark.asyncio
async def test_workspace_from_name(owner: "ServerUser"):
    workspace = await WorkspaceFactory.create(name="test_workspace")
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)
    ArgillaSingleton.init(api_key=owner.api_key)

    found_workspace = Workspace.from_name(workspace.name)
    assert found_workspace.name == workspace.name
    assert isinstance(found_workspace.id, UUID)

    with pytest.raises(ValueError, match="Workspace with name="):
        Workspace.from_name("non-existing-workspace")


@pytest.mark.asyncio
async def test_workspace_from_id(owner: "ServerUser"):
    workspace = await WorkspaceFactory.create(name="test_workspace")
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
    workspaces = api.http_client.get("/api/v1/me/workspaces")["items"]
    assert any(ws["name"] == "test_workspace" for ws in workspaces)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_workspace_create_not_allowed_role(role: UserRole) -> None:
    user = await UserFactory.create(role=role)
    ArgillaSingleton.init(api_key=user.api_key)

    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `create`"):
        Workspace.create(name="test_workspace")


@pytest.mark.asyncio
async def test_workspace_list(owner: "ServerUser") -> None:
    await WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    workspaces = Workspace.list()
    assert any(ws.name == "test_workspace" for ws in workspaces)


@pytest.mark.asyncio
async def test_workspace_users(owner: "ServerUser") -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name(name=workspace.name)
    assert all(isinstance(user, UserModel) for user in workspace.users)


@pytest.mark.parametrize("role", [UserRole.annotator])
@pytest.mark.asyncio
async def test_workspace_users_not_allowed_role(role: UserRole) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    user = await UserFactory.create(role=role, workspaces=[workspace])
    ArgillaSingleton.init(api_key=user.api_key)

    workspace = Workspace.from_name(name=workspace.name)
    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `users`"):
        workspace.users


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_workspace_add_user(owner: "ServerUser", role: UserRole) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    new_user = await UserFactory.create(role=role)
    workspace.add_user(new_user.id)
    assert any(user.username == new_user.username for user in workspace.users)

    with pytest.raises(ValueError, match="User with id="):
        workspace.add_user(new_user.id)

    workspace = Workspace.from_name("test_workspace")
    assert isinstance(workspace.users, list)
    assert any(user.username == new_user.username for user in workspace.users)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_workspace_add_user_not_allowed_role(role: UserRole) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    user = await UserFactory.create(role=role, workspaces=[workspace])
    ArgillaSingleton.init(api_key=user.api_key)

    workspace = Workspace.from_name(workspace.name)
    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `add_user`"):
        workspace.add_user(user.id)


@pytest.mark.asyncio
async def test_workspace_add_user_warnings(owner: "ServerUser") -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    with pytest.warns(UserWarning, match="The user you are trying to add to the workspace has the `owner` role"):
        workspace.add_user(owner.id)
    assert workspace.users == []


@pytest.mark.asyncio
async def test_workspace_add_user_errors(owner: "ServerUser") -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    wrong_user_id = uuid4()
    with pytest.raises(ValueError, match=f"User with id=\`{wrong_user_id}\` doesn't exist in Argilla"):
        workspace.add_user(wrong_user_id)
    assert workspace.users == []

    valid_user = await UserFactory.create(role=UserRole.annotator)
    workspace.add_user(valid_user.id)
    with pytest.raises(ValueError, match=f"User with id=\`{valid_user.id}\` already exists in workspace"):
        workspace.add_user(valid_user.id)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_workspace_delete_user(owner: "ServerUser", role: UserRole) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    new_user = await UserFactory.create(role=role)
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=new_user.id)
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert any(user.username == new_user.username for user in workspace.users)

    workspace.delete_user(new_user.id)
    assert not any(user.username == new_user.username for user in workspace.users)

    with pytest.raises(ValueError, match="Either the user with id="):
        workspace.delete_user(new_user.id)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_workspace_delete_user_not_allowed_role(role: UserRole) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    user = await UserFactory.create(role=role, workspaces=[workspace])
    ArgillaSingleton.init(api_key=user.api_key)

    workspace = Workspace.from_name(workspace.name)
    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `delete_user`"):
        workspace.delete_user(user.id)


@pytest.mark.asyncio
async def test_workspace_delete_user_warnings(owner: "ServerUser") -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    with pytest.warns(UserWarning, match="The user you are trying to delete from the workspace has the `owner` role"):
        workspace.delete_user(owner.id)
    assert workspace.users == []


@pytest.mark.asyncio
async def test_workspace_delete_user_errors(owner: "ServerUser") -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    new_user = await UserFactory.create(role=UserRole.annotator)
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=new_user.id)
    ArgillaSingleton.init(api_key=owner.api_key)

    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, UUID)

    wrong_user_id = uuid4()
    with pytest.raises(ValueError, match=f"User with id=\`{wrong_user_id}\` doesn't exist in Argilla"):
        workspace.delete_user(wrong_user_id)

    workspace.delete_user(new_user.id)
    with pytest.raises(
        ValueError,
        match=f"Either the user with id=\`{new_user.id}\` doesn't exist in Argilla, or it doesn't belong to workspace with id=\`{workspace.id}\`",
    ):
        workspace.delete_user(new_user.id)


@pytest.mark.asyncio
async def test_print_workspace(owner: "ServerUser"):
    workspace = await WorkspaceFactory.create(name="test_workspace")
    ArgillaSingleton.init(api_key=owner.api_key)

    assert str(Workspace.from_name(workspace.name)) == (
        f"Workspace(id={workspace.id}, name={workspace.name}, "
        f"inserted_at={workspace.inserted_at}, updated_at={workspace.updated_at})"
    )


def test_set_new_workspace(owner: "ServerUser"):
    ArgillaSingleton.init(api_key=owner.api_key)
    ws = Workspace.create("new-workspace")

    ArgillaSingleton.get().set_workspace(ws.name)
    assert ArgillaSingleton.get().get_workspace() == ws.name


@pytest.mark.asyncio
async def test_init_with_workspace(owner: "ServerUser"):
    workspace = await WorkspaceFactory.create(name="test_workspace")

    ArgillaSingleton.init(api_key=owner.api_key, workspace=workspace.name)

    assert ArgillaSingleton.get().get_workspace() == workspace.name


def test_set_workspace_with_missing_workspace(owner: "ServerUser"):
    ArgillaSingleton.init(api_key=owner.api_key)
    with pytest.raises(ValueError):
        ArgillaSingleton.get().set_workspace("missing-workspace")


def test_init_with_missing_workspace(owner: "ServerUser"):
    with pytest.raises(ValueError):
        ArgillaSingleton.init(api_key=owner.api_key, workspace="missing-workspace")


@pytest.mark.asyncio
async def test_delete_workspace(owner: "ServerUser"):
    workspace = await WorkspaceFactory.create(name="test_workspace")

    ArgillaSingleton.init(api_key=owner.api_key)

    ws = Workspace.from_id(workspace.id)
    ws.delete()

    with pytest.raises(ValueError, match=rf"Workspace with id=`{ws.id}` doesn't exist in Argilla"):
        Workspace.from_id(workspace.id)


@pytest.mark.asyncio
async def test_delete_non_existing_workspace(owner: "ServerUser"):
    workspace = await WorkspaceFactory.create(name="test_workspace")

    ArgillaSingleton.init(api_key=owner.api_key)

    ws = Workspace.from_id(workspace.id)
    ws.delete()

    with pytest.raises(ValueError, match=rf"Workspace with id {ws.id} doesn't exist in Argilla."):
        ws.delete()


@pytest.mark.asyncio
async def test_delete_workspace_with_linked_datasets(owner: "ServerUser"):
    workspace = await WorkspaceFactory.create(name="test_workspace")
    await DatasetFactory.create(workspace=workspace)

    ArgillaSingleton.init(api_key=owner.api_key)

    ws = Workspace.from_id(workspace.id)
    with pytest.raises(
        ValueError,
        match=rf"Cannot delete workspace with id {ws.id}. Some datasets are still linked to this workspace.",
    ):
        ws.delete()


@pytest.mark.asyncio
async def test_delete_workspace_without_permissions():
    workspace = await WorkspaceFactory.create(name="test_workspace")

    user = await UserFactory.create(workspaces=[workspace])

    ArgillaSingleton.init(api_key=user.api_key)

    ws = Workspace.from_id(workspace.id)

    with pytest.raises(PermissionError, match=rf"User with role={user.role.value} is not allowed to call `delete`"):
        ws.delete()
