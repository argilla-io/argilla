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
from unittest.mock import ANY

import pytest
from rich.table import Table

if TYPE_CHECKING:
    from argilla_v1.client.users import User
    from argilla_v1.client.workspaces import Workspace
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
class TestSuiteListUsersCommand:
    def test_list_users(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", user: "User") -> None:
        add_row_spy = mocker.spy(Table, "add_row")
        user_list_mock = mocker.patch("argilla_v1.client.users.User.list", return_value=[user])

        result = cli_runner.invoke(cli, "users list")

        assert result.exit_code == 0
        user_list_mock.assert_called_once()
        add_row_spy.assert_called_once_with(
            ANY,
            str(user.id),
            user.username,
            user.role,
            user.first_name,
            user.last_name,
            "• unit-test",
            user.inserted_at.isoformat(sep=" "),
            user.updated_at.isoformat(sep=" "),
        )

    def test_list_users_with_workspace(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", user: "User", workspace: "Workspace"
    ) -> None:
        add_row_spy = mocker.spy(Table, "add_row")
        workspace_from_name_mock = mocker.patch(
            "argilla_v1.client.workspaces.Workspace.from_name", return_value=workspace
        )
        mocker.patch("argilla_v1.client.workspaces.Workspace.users", new_callable=lambda: [user])

        result = cli_runner.invoke(cli, "users list --workspace unit-test")

        assert result.exit_code == 0
        workspace_from_name_mock.assert_called_once_with("unit-test")
        add_row_spy.assert_called_once_with(
            ANY,
            str(user.id),
            user.username,
            user.role,
            user.first_name,
            user.last_name,
            "• unit-test",
            user.inserted_at.isoformat(sep=" "),
            user.updated_at.isoformat(sep=" "),
        )

    def test_list_users_with_role(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", user: "User"
    ) -> None:
        add_row_spy = mocker.spy(Table, "add_row")
        user_list_mock = mocker.patch("argilla_v1.client.users.User.list", return_value=[user])

        result = cli_runner.invoke(cli, "users list --role annotator")

        assert result.exit_code == 0
        user_list_mock.assert_called_once()
        add_row_spy.assert_not_called()


@pytest.mark.usefixtures("not_logged_mock")
def test_list_users_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "users delete unit-test")

    assert result.exit_code == 1
    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
