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

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


def test_login(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    login_mock = mocker.patch("argilla_v1.client.login.login")

    result = cli_runner.invoke(
        cli,
        'login --api-url http://localhost:6900 --api-key api.key --workspace my_workspace --extra-headers "{\\"X-Unit-Test\\": \\"true\\"}"',
    )

    assert result.exit_code == 0
    login_mock.assert_called_once_with(
        api_url="http://localhost:6900",
        api_key="api.key",
        workspace="my_workspace",
        extra_headers={"X-Unit-Test": "true"},
    )


def test_login_fails(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    login_mock = mocker.patch("argilla_v1.client.login.login")
    login_mock.side_effect = ValueError

    result = cli_runner.invoke(
        cli,
        'login --api-url http://localhost:6900 --api-key api.key --workspace my_workspace --extra-headers "{\\"X-Unit-Test\\": \\"true\\"}"',
    )

    assert result.exit_code == 1
    login_mock.assert_called_once_with(
        api_url="http://localhost:6900",
        api_key="api.key",
        workspace="my_workspace",
        extra_headers={"X-Unit-Test": "true"},
    )


def test_login_with_invalid_extra_headers(cli_runner: "CliRunner", cli: "Typer"):
    result = cli_runner.invoke(
        cli,
        'login --api-url http://localhost:6900 --api-key api.key --workspace my_workspace --extra-headers "{\\"X-Unit-Test\\": \\"true\\""',
    )

    assert result.exit_code == 1
