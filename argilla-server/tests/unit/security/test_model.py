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

from typing import Union

import pytest
from argilla_server.schemas.v0.users import User, UserCreate
from argilla_server.schemas.v0.workspaces import WorkspaceCreate

from tests.factories import UserFactory, WorkspaceFactory
from tests.pydantic_v1 import ValidationError


@pytest.mark.parametrize("invalid_name", ["work space", "work/space", "work.space", "_", "-"])
def test_workspace_create_invalid_name(invalid_name: str):
    with pytest.raises(ValidationError):
        WorkspaceCreate(name=invalid_name)


@pytest.mark.parametrize(
    "username",
    [
        "user-name",
        "user_name",
        "user123",
        "user-123",
        "user_123",
        "UserName",
        "userName",
        "User_name",
        "valid_user_name",
        "user-123_abc",
        "user_123-abc",
        "0033_user",
        "12-user",
    ],
)
def test_user_create(username: str):
    assert UserCreate(first_name="first-name", username=username, password="12345678")


@pytest.mark.parametrize(
    "invalid_username",
    [
        "user name",
        "user/name",
        "user.name",
        "_",
        "-",
        "-1234",
        "_1234",
        "_mark",
        "-mark",
    ],
)
def test_user_create_invalid_username(invalid_username: str):
    with pytest.raises(ValidationError):
        UserCreate(first_name="first-name", username=invalid_username, password="12345678")


@pytest.mark.asyncio
async def test_user_first_name():
    user = await UserFactory.create(first_name="first-name", workspaces=[])

    assert User.from_orm(user).first_name == "first-name"


@pytest.mark.asyncio
async def test_user_last_name():
    user = await UserFactory.create(last_name="last-name", workspaces=[])

    assert User.from_orm(user).last_name == "last-name"


@pytest.mark.asyncio
async def test_user_full_name():
    user = await UserFactory.create(first_name="first-name", last_name="last-name", workspaces=[])

    assert User.from_orm(user).full_name == "first-name last-name"


@pytest.mark.parametrize("last_name", [None, ""])
@pytest.mark.asyncio
async def test_user_full_name_without_last_name(last_name: Union[str, None]):
    user = await UserFactory.create(first_name="first-name", last_name=last_name, workspaces=[])

    assert User.from_orm(user).full_name == "first-name"


@pytest.mark.asyncio
async def test_user_workspaces():
    workspace_a = await WorkspaceFactory.create(name="workspace-a")
    workspace_b = await WorkspaceFactory.create(name="workspace-b")
    user = await UserFactory.create(workspaces=[workspace_a, workspace_b])

    assert User.from_orm(user).workspaces == ["workspace-a", "workspace-b"]
