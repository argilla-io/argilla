import pytest

from rubrix.server.commons.errors import ForbiddenOperationError
from rubrix.server.security.model import User


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


@pytest.mark.parametrize(
    "workspaces, expected",
    [
        (None, []),
        (["a"], ["a", "user"]),
        ([], ["user"]),
    ],
)
def test_check_team_with_default(workspaces, expected):
    user = User(username="user", workspaces=workspaces)
    assert user.check_workspaces([]) == expected
