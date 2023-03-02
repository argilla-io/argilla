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
import uuid
from datetime import datetime

import pytest
from argilla.server.errors import EntityNotFoundError
from argilla.server.security.model import User, UserCreate, WorkspaceCreate
from pydantic import ValidationError


@pytest.mark.parametrize("wrong_name", ["user name", "user/name", "user.name", "UserName", "userName"])
def test_username_validator(wrong_name):
    with pytest.raises(ValidationError):
        UserCreate(username=wrong_name, password="12345678", first_name="Test")


@pytest.mark.parametrize("wrong_workspace", ["work space", "work/space", "work.space", "_", "-"])
def test_workspace_validator(wrong_workspace):
    with pytest.raises(ValidationError):
        WorkspaceCreate(name=wrong_workspace)


def test_check_non_provided_workspaces():
    user = User(
        username="test",
        api_key="api-key",
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    user.is_superuser()
    assert user.check_workspaces([]) == ["test"]

    user = User(
        username="test",
        workspaces=["ws"],
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        api_key="api-key",
    )
    assert set(user.check_workspaces([])) == {"ws", "test"}

    with pytest.raises(EntityNotFoundError, match="not-found"):
        assert user.check_workspaces(["ws", "not-found"])


def test_check_user_workspaces():
    a_ws = "A-workspace"
    expected_workspaces = [a_ws, "B-ws"]
    user = User(
        username="test-user",
        api_key="api-key",
        workspaces=[a_ws, "B-ws", "C-ws"],
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    assert user.check_workspace(a_ws) == a_ws
    assert user.check_workspaces(expected_workspaces) == expected_workspaces
    with pytest.raises(EntityNotFoundError):
        assert user.check_workspaces(["not-found-ws"])


def test_default_workspace():
    user = User(
        username="admin",
        api_key="api-key",
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert user.default_workspace == "admin"

    test_user = User(
        username="test",
        api_key="api-key",
        workspaces=["ws"],
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert test_user.default_workspace == test_user.username


def test_workspace_for_superuser():
    user = User(
        username="admin",
        api_key="api-key",
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert user.default_workspace == "admin"

    with pytest.raises(EntityNotFoundError):
        assert user.check_workspace("some") == "some"

    assert user.check_workspace(None) == "admin"
    assert user.check_workspace("") == "admin"

    user.workspaces = ["some"]
    assert user.check_workspaces(["some"]) == ["some"]


def test_workspaces_with_default():
    expected_workspaces = ["user", "ws1"]
    user = User(
        username="user",
        workspaces=expected_workspaces,
        api_key="api-key",
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert len(user.workspaces) == len(expected_workspaces)
    for ws in expected_workspaces:
        assert ws in user.workspaces


def test_is_superuser():
    admin_user = User(
        username="admin",
        api_key="api-key",
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert admin_user.is_superuser()

    admin_user.workspaces.append("other-workspace")
    assert admin_user.is_superuser()
    assert set(admin_user.workspaces) == {"other-workspace", "admin"}

    user = User(
        username="test",
        workspaces=["bod"],
        api_key="api-key",
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert not user.is_superuser()
    user.superuser = True
    assert user.is_superuser()


@pytest.mark.parametrize(
    "workspaces, expected",
    [
        (None, {"user"}),
        ([], {"user"}),
        (["a"], {"user", "a"}),
    ],
)
def test_check_workspaces_with_default(workspaces, expected):
    user = User(
        username="user",
        workspaces=workspaces,
        api_key="api-key",
        id=uuid.uuid4(),
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert set(user.check_workspaces([])) == expected
    assert set(user.check_workspaces(None)) == expected
    assert set(user.check_workspaces([None])) == expected
    assert user.check_workspace(user.username) == user.username
