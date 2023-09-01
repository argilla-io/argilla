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

from typing import TYPE_CHECKING, Type

import pytest

if TYPE_CHECKING:
    from argilla.client.users import User
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
class TestSuiteDeleteUserCommand:
    def test_delete_user(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", user: "User") -> None:
        user_from_name_mock = mocker.patch("argilla.client.users.User.from_name", return_value=user)
        user_delete_mock = mocker.patch("argilla.client.users.User.delete")

        result = cli_runner.invoke(cli, "users delete unit-test")

        assert result.exit_code == 0
        assert "User removed" in result.stdout
        assert "User with username 'unit-test' has been removed!" in result.stdout
        user_from_name_mock.assert_called_once_with("unit-test")
        user_delete_mock.assert_called_once()

    @pytest.mark.parametrize(
        "ExceptionType, expected_msg",
        [
            (ValueError, "User with username 'unit-test' doesn't exist!"),
            (RuntimeError, "An unexpected error occurred when trying to remove the user"),
        ],
    )
    def test_delete_user_errors(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        ExceptionType: Type[Exception],
        expected_msg: str,
    ) -> None:
        user_from_name_mock = mocker.patch("argilla.client.users.User.from_name", side_effect=ExceptionType)
        result = cli_runner.invoke(cli, "users delete unit-test")

        assert result.exit_code == 1
        assert expected_msg in result.stdout
        user_from_name_mock.assert_called_once_with("unit-test")


@pytest.mark.usefixtures("not_logged_mock")
def test_delete_user_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "users delete unit-test")

    assert result.exit_code == 1
    assert "You are not logged in. Please run `argilla login` to login to an Argilla server." in result.stdout
