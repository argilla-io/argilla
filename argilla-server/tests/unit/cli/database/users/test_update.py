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

import pytest
from argilla_server.models import User, UserRole
from click.testing import CliRunner
from typer import Typer

from tests.factories import UserSyncFactory

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@pytest.mark.parametrize("new_role_string", ["owner", "admin"])
def test_update(sync_db: "Session", cli_runner: CliRunner, cli: Typer, new_role_string: str):
    user = UserSyncFactory.create(username="username", role=UserRole.annotator)

    result = cli_runner.invoke(cli, f"database users update username --role {new_role_string}")

    assert result.exit_code == 0

    # user = (await db.execute(select(User).filter_by(username="username"))).scalar_one_or_none()
    user = sync_db.query(User).filter_by(username="username").first()
    assert user.role.value == UserRole(new_role_string).value


def test_update_with_invalid_role(cli_runner: CliRunner, cli: Typer):
    bad_role_str = "bad-role"
    result = cli_runner.invoke(cli, f"database users update username --role {bad_role_str}")

    assert result.exit_code == 2
    assert f"{bad_role_str!r} is not one of" in result.output, result.output


def test_update_with_missing_username(cli_runner: CliRunner, cli: Typer):
    missing_username = "missing-username"
    result = cli_runner.invoke(cli, f"database users update {missing_username} --role owner")

    assert result.exit_code == 0
    assert result.output == f"User with username {missing_username!r} does not exists in database. Skipping...\n"


@pytest.mark.parametrize("role_string", ["owner", "admin", "annotator"])
def test_update_with_same_user_role(cli_runner: CliRunner, cli: Typer, role_string: str):
    username = "username"
    UserSyncFactory.create(username=username, role=UserRole(role_string))

    result = cli_runner.invoke(cli, f"database users update {username} --role {role_string}")

    assert result.exit_code == 0
    assert result.output == f"User {username!r} already has role {role_string!r}. Skipping...\n"
