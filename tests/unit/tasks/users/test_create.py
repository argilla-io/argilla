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

from datetime import datetime
from typing import TYPE_CHECKING, Type
from uuid import uuid4

import httpx
import pytest
from argilla.client.sdk.users.models import UserRole
from argilla.client.users import User

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.fixture
def user() -> User:
    user = User.__new__(User)
    user.__dict__.update(
        {
            "_client": httpx.Client(),
            "id": uuid4(),
            "username": "unit-test",
            "last_name": "unit-test",
            "first_name": "unit-test",
            "role": UserRole.owner,
            "api_key": "apikey.unit-test",
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )
    return user


@pytest.mark.usefixtures("login_mock")
class TestSuiteCreateUserCommand:
    def test_create_user(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", user: User) -> None:
        user_create_mock = mocker.patch("argilla.client.users.User.create", return_value=user)
        mocker.patch("argilla.client.users.User.workspaces", return_value=["ws1", "ws2"])

        result = cli_runner.invoke(
            cli,
            "users create --username unit-test --password unit-test --first-name unit-test --last-name unit-test --role owner --workspace ws1 --workspace ws2",
        )

        assert result.exit_code == 0
        assert "User created" in result.stdout
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
            (KeyError, "User with 'unit-test' already exists!"),
            (ValueError, "Provided parameters are not valid"),
            (RuntimeError, "An error ocurred when trying to create the user"),
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
        user_create_mock = mocker.patch("argilla.client.users.User.create", side_effect=ExceptionType)

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
