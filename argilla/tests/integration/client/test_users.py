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
from argilla_v1.client.sdk.users.models import UserRole
from argilla_v1.client.sdk.v1.workspaces.models import WorkspaceModel as WorkspaceModelV1
from argilla_v1.client.sdk.workspaces.models import WorkspaceModel as WorkspaceModelV0
from argilla_v1.client.singleton import ArgillaSingleton
from argilla_v1.client.users import User

if TYPE_CHECKING:
    from argilla_server.models import User as ServerUser

from tests.factories import UserFactory, WorkspaceFactory


def test_user_cls_init() -> None:
    with pytest.raises(
        Exception,
        match=r"`User` cannot be initialized via the `__init__` method | you should use `User.from_name\('test_user'\)`",
    ):
        User(name="test_user")

    with pytest.raises(
        Exception,
        match=r"`User` cannot be initialized via the `__init__` method | you should use `User.from_id\('00000000-0000-0000-0000-000000000000'\)`",
    ):
        User(id="00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_user_from_name(owner: "ServerUser") -> None:
    new_user = await UserFactory.create(username="test_user")
    ArgillaSingleton.init(api_key=owner.api_key)

    user = User.from_name(new_user.username)
    assert user.username == new_user.username
    assert isinstance(user.id, UUID)

    with pytest.raises(ValueError, match="User with username="):
        User.from_name("non-existing-user")


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_from_name_not_allowed_role(role: UserRole) -> None:
    user = await UserFactory.create(role=role)
    ArgillaSingleton.init(api_key=user.api_key)

    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `from_name`"):
        User.from_name(name=user.username)


@pytest.mark.asyncio
async def test_user_from_id(owner: "ServerUser") -> None:
    new_user = await UserFactory.create(username="test_user")
    ArgillaSingleton.init(api_key=owner.api_key)

    user = User.from_id(id=new_user.id)
    assert user.username == "test_user"
    assert isinstance(user.id, UUID)

    with pytest.raises(ValueError, match="User with id="):
        User.from_id(id="00000000-0000-0000-0000-000000000000")


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_from_id_not_allowed_role(role: UserRole) -> None:
    user = await UserFactory.create(role=role)
    ArgillaSingleton.init(api_key=user.api_key)

    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `from_id`"):
        User.from_id(id=user.id)


def test_user_me(owner: "ServerUser") -> None:
    ArgillaSingleton.init(api_key=owner.api_key)

    user = User.me()
    assert user.id == owner.id
    assert user.username == owner.username


@pytest.mark.asyncio
async def test_user_create(owner: "ServerUser") -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")

    ArgillaSingleton.init(api_key=owner.api_key)

    with pytest.warns(UserWarning):
        new_user = User.create("test_user", password="test_password", workspaces=["test_workspace"])
        assert new_user.first_name == "test_user"
        assert new_user.last_name is None
        assert new_user.full_name == "test_user"
        assert new_user.username == "test_user"
        assert new_user.workspaces == [
            WorkspaceModelV1(
                id=workspace.id,
                name=workspace.name,
                inserted_at=workspace.inserted_at,
                updated_at=workspace.updated_at,
            )
        ]

    with pytest.raises(KeyError, match="already exists in Argilla"):
        User.create("test_user", password="test_password")


def test_user_create_with_non_existent_workspace(owner: "ServerUser") -> None:
    ArgillaSingleton.init(api_key=owner.api_key)

    with pytest.raises(ValueError, match="^(.*)Workspace 'non_existent_workspace' does not exist$"):
        User.create("test_user", password="test_password", workspaces=["non_existent_workspace"])


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_create_not_allowed_role(role: UserRole) -> None:
    user = await UserFactory.create(role=role)
    ArgillaSingleton.init(api_key=user.api_key)

    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `create`"):
        User.create("test_user", password="test_password", role=role)


@pytest.mark.asyncio
async def test_user_list(owner: "ServerUser") -> None:
    await UserFactory.create(username="user_1")
    await UserFactory.create(username="user_2")
    ArgillaSingleton.init(api_key=owner.api_key)

    users = User.list()
    assert all(user.username in ["user_1", "user_2", owner.username] for user in users)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_list_not_allowed_role(role: UserRole) -> None:
    user = await UserFactory.create(role=role)
    ArgillaSingleton.init(api_key=user.api_key)

    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `list`"):
        User.list()


@pytest.mark.asyncio
async def test_user_delete_user(owner: "ServerUser") -> None:
    new_user = await UserFactory.create(username="test_user")
    ArgillaSingleton.init(api_key=owner.api_key)

    user = User.from_name("test_user")
    assert user.username == new_user.username

    user.delete()
    with pytest.raises(ValueError, match="doesn't exist in Argilla"):
        user.delete()


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_delete_not_allowed_role(role: UserRole) -> None:
    user = await UserFactory.create(role=role)
    ArgillaSingleton.init(api_key=user.api_key)

    user = User.me()
    with pytest.raises(PermissionError, match=f"User with role={role} is not allowed to call `delete`"):
        user.delete()


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_repr(role: UserRole) -> None:
    user = await UserFactory.create(role=role)
    ArgillaSingleton.init(api_key=user.api_key)

    assert str(User.me()) == (
        f"User(id={user.id}, username={user.username}, role={user.role},"
        f" api_key={user.api_key}, first_name={user.first_name},"
        f" last_name={user.last_name}, inserted_at={user.inserted_at},"
        f" updated_at={user.updated_at})"
    )


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_workspaces(role: UserRole) -> None:
    workspaces = await WorkspaceFactory.create_batch(3)
    user = await UserFactory.create(role=role, workspaces=workspaces)
    ArgillaSingleton.init(api_key=user.api_key)

    user = User.me()
    assert isinstance(user.workspaces, list)
    assert len(user.workspaces) == len(workspaces)
    assert all(isinstance(workspace, (WorkspaceModelV0, WorkspaceModelV1)) for workspace in user.workspaces)
    assert [workspace.name for workspace in workspaces] == [workspace.name for workspace in user.workspaces]


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_user_workspaces_from_owner_to_any(owner: "ServerUser", role: UserRole) -> None:
    workspaces = await WorkspaceFactory.create_batch(3)
    user = await UserFactory.create(role=role, workspaces=workspaces)
    ArgillaSingleton.init(api_key=owner.api_key)

    user = User.from_name(user.username)
    assert isinstance(user.workspaces, list)
    assert len(user.workspaces) == len(workspaces)
    assert all(isinstance(workspace, (WorkspaceModelV0, WorkspaceModelV1)) for workspace in user.workspaces)
    assert [workspace.name for workspace in workspaces] == [workspace.name for workspace in user.workspaces]


@pytest.mark.parametrize(
    "role, is_owner, is_admin, is_annotator",
    [
        (UserRole.owner, True, False, False),
        (UserRole.admin, False, True, False),
        (UserRole.annotator, False, False, True),
    ],
)
@pytest.mark.asyncio
async def test_user_role_property(
    role: UserRole, owner: "ServerUser", is_owner: bool, is_admin: bool, is_annotator: bool
) -> None:
    user = await UserFactory.create(role=role)

    ArgillaSingleton.init(api_key=owner.api_key)

    user = User.from_name(user.username)
    assert user.is_owner == is_owner
    assert user.is_admin == is_admin
    assert user.is_annotator == is_annotator
