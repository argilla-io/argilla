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


@pytest.mark.parametrize(
    "teams, expected",
    [
        (None, []),
        (["a"], ["a", "user"]),
        ([], ["user"]),
    ],
)
def test_check_team_with_default(teams, expected):
    user = User(username="user", teams=teams)
    assert user.check_teams([]) == expected
