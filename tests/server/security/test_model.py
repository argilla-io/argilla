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
