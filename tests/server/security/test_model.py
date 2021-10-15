import pytest

from rubrix.server.commons.errors import ForbiddenOperationError
from rubrix.server.security.model import User


def test_check_user_teams():

    a_team = "A-team"
    expected_teams = [a_team, "B-team"]
    user = User(username="test-user", teams=[a_team, "B-team", "C-team"])

    assert user.check_team(a_team) == a_team
    assert user.check_teams(expected_teams) == expected_teams
    with pytest.raises(ForbiddenOperationError):
        assert user.check_teams(["not-found-team"])


def test_default_team():

    user = User(username="admin")
    assert user.default_team == None

    test_user = User(username="test", teams=["team"])
    assert test_user.default_team == test_user.username


def test_check_team_with_default():
    admin = User(username="admin")
    assert admin.check_teams([]) == []

    test_user = User(username="test", teams=["a"])
    assert test_user.check_teams([]) == ["a", test_user.username]
