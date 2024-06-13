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
from argilla_v1.client.sdk.users.models import UserRole

if TYPE_CHECKING:
    from argilla_v1.client.users import User
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
class TestSuiteCreateUserCommand:
    def test_create_user(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", user: "User") -> None:
        user_create_mock = mocker.patch("argilla_v1.client.users.User.create", return_value=user)

        result = cli_runner.invoke(
            cli,
            "users create --username unit-test --password unit-test --first-name unit-test --last-name unit-test --role owner --workspace ws1 --workspace ws2",
        )

        assert result.exit_code == 0
        assert "User created" in result.stdout
        assert "Username: unit-test" in result.stdout
        assert "Role: admin" in result.stdout
        assert "First name: unit-test" in result.stdout
        assert "Last name: unit-test" in result.stdout
        assert "Workspaces: unit-test" in result.stdout
        user_create_mock.assert_called_once_with(
            username="unit-test",
            password="unit-test",
            first_name="unit-test",
            last_name="unit-test",
            role=UserRole.owner,
            workspaces=["ws1", "ws2"],
        )

    @pytest.mark.parametrize(
        "ExceptionType, expected_msg",
        [
            (KeyError, "User with name=unit-test already exists"),
            (ValueError, "Provided parameters are not valid"),
            (RuntimeError, "An unexpected error occurred when trying to create the user"),
        ],
    )
    def test_create_user_errors(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        ExceptionType: Type[Exception],
        expected_msg: str,
    ) -> None:
        user_create_mock = mocker.patch("argilla_v1.client.users.User.create", side_effect=ExceptionType)

        result = cli_runner.invoke(
            cli,
            "users create --username unit-test --password unit-test --first-name unit-test --last-name unit-test --role owner --workspace ws1 --workspace ws2",
        )

        assert result.exit_code == 1
        assert expected_msg in result.stdout
        user_create_mock.assert_called_once_with(
            username="unit-test",
            password="unit-test",
            first_name="unit-test",
            last_name="unit-test",
            role=UserRole.owner,
            workspaces=["ws1", "ws2"],
        )


@pytest.mark.usefixtures("not_logged_mock")
def test_create_user_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "users create --username unit-test --password unit-test")

    assert result.exit_code == 1
    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
