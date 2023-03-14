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
from argilla.server.errors import BadRequestError, EntityNotFoundError
from argilla.server.security.model import User
from pydantic import ValidationError


@pytest.mark.parametrize("email", ["my@email.com", "infra@argilla.io"])
def test_valid_mail(email):
    user = User(username="user", email=email)
    assert user.email == email


@pytest.mark.parametrize("wrong_email", ["non-valid-email", "wrong@mail", "@wrong" "wrong.mail"])
def test_email_validator(wrong_email):
    with pytest.raises(ValidationError):
        User(username="user", email=wrong_email)


@pytest.mark.parametrize("wrong_name", ["user name", "user/name", "user.name", "UserName", "userName"])
def test_username_validator(wrong_name):
    with pytest.raises(
        ValidationError,
        match=f"Wrong username. The username {wrong_name} does not match the pattern",
    ):
        User(username=wrong_name)


@pytest.mark.parametrize("wrong_workspace", ["work space", "work/space", "work.space", "_", "-"])
def test_workspace_validator(wrong_workspace):
    with pytest.raises(ValidationError):
        User(username="username", workspaces=[wrong_workspace])


def test_check_non_provided_workspaces():
    user = User(username="test")
    assert user.check_workspaces([]) == ["test"]

    user = User(username="test", workspaces=["ws"])
    assert set(user.check_workspaces([])) == {"ws", "test"}

    with pytest.raises(EntityNotFoundError, match="not-found"):
        assert user.check_workspaces(["ws", "not-found"])


def test_check_user_workspaces():
    a_ws = "A-workspace"
    expected_workspaces = [a_ws, "B-ws"]
    user = User(username="test-user", workspaces=[a_ws, "B-ws", "C-ws"])

    assert user.check_workspace(a_ws) == a_ws
    assert user.check_workspaces(expected_workspaces) == expected_workspaces
    with pytest.raises(EntityNotFoundError):
        assert user.check_workspaces(["not-found-ws"])


def test_workspace_for_superuser():
    user = User(username="admin")

    assert user.check_workspace("admin") == "admin"

    with pytest.raises(EntityNotFoundError):
        assert user.check_workspace("some") == "some"

    user.workspaces = ["some"]
    assert user.check_workspaces(["some"]) == ["some"]


def test_workspaces_with_default():
    expected_workspaces = ["user", "ws1"]
    user = User(username="user", workspaces=expected_workspaces)
    assert len(user.workspaces) == len(expected_workspaces)
    for ws in expected_workspaces:
        assert ws in user.workspaces


def test_is_superuser():
    admin_user = User(username="admin")
    assert admin_user.is_superuser()

    admin_user.workspaces.append("other-workspace")
    assert admin_user.is_superuser()
    assert set(admin_user.workspaces) == {"other-workspace", "admin"}

    user = User(username="test", workspaces=["bod"])
    assert not user.is_superuser()
    user.superuser = True
    assert user.is_superuser()


@pytest.mark.parametrize("workspaces", [None, [], ["a"]])
def test_check_workspaces_with_default(workspaces):
    user = User(username="user", workspaces=workspaces)
    assert set(user.check_workspace(user.username)) == set(user.username)


@pytest.mark.parametrize(
    "user",
    [
        User(username="admin", workspaces=None, superuser=True),
        User(username="mock", workspaces=None, superuser=False),
        User(username="user", workspaces=["ab"], superuser=True),
    ],
)
def test_check_workspace_without_workspace(user):
    assert user.check_workspace("") == user.username
    assert user.check_workspace(None) == user.username
