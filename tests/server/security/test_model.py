import pytest
from pydantic import ValidationError

from rubrix.server.commons.errors import ForbiddenOperationError
from rubrix.server.security.model import User


@pytest.mark.parametrize("email", ["my@email.com", "infra@recogn.ai"])
def test_valid_mail(email):
    user = User(username="user", email=email)
    assert user.email == email


@pytest.mark.parametrize(
    "wrong_email", ["non-valid-email", "wrong@mail", "@wrong" "wrong.mail"]
)
def test_email_validator(wrong_email):
    with pytest.raises(ValidationError):
        User(username="user", email=wrong_email)


@pytest.mark.parametrize("wrong_name", ["user name", "user/name", "user.name"])
def test_username_validator(wrong_name):
    with pytest.raises(ValidationError):
        User(username=wrong_name)


@pytest.mark.parametrize("wrong_workspace", ["work space", "work/space", "work.space"])
def test_workspace_validator(wrong_workspace):
    with pytest.raises(ValidationError):
        User(username="username", workspaces=[wrong_workspace])


def test_check_non_provided_workspaces():
    user = User(username="test")
    assert not user.check_workspaces([])  # super-user

    user.workspaces = ["ws"]
    assert user.check_workspaces([]) == [user.default_workspace]

    with pytest.raises(ForbiddenOperationError, match="not-found"):
        assert user.check_workspaces(["ws", "not-found"])


def test_check_user_workspaces():

    a_ws = "A-workspace"
    expected_workspaces = [a_ws, "B-ws"]
    user = User(username="test-user", workspaces=[a_ws, "B-ws", "C-ws"])

    assert user.check_workspace(a_ws) == a_ws
    assert user.check_workspaces(expected_workspaces) == expected_workspaces
    with pytest.raises(ForbiddenOperationError):
        assert user.check_workspaces(["not-found-ws"])


def test_default_workspace():

    user = User(username="admin")
    assert user.default_workspace is None

    test_user = User(username="test", workspaces=["ws"])
    assert test_user.default_workspace == test_user.username


def test_workspace_for_superuser():
    user = User(username="admin")
    assert user.default_workspace is None

    assert user.check_workspace("some") == "some"
    assert user.check_workspaces(["some"]) == ["some"]

@pytest.mark.parametrize(
    "workspaces, expected",
    [
        (None, []),
        ([], ["user"]),
        (["a"], ["user"]),
    ],
)
def test_check_workspaces_with_default(workspaces, expected):
    user = User(username="user", workspaces=workspaces)
    assert user.check_workspaces([]) == expected
    assert user.check_workspaces(None) == expected
    assert user.check_workspaces([None]) == expected
    assert user.check_workspace(user.username) == user.username
