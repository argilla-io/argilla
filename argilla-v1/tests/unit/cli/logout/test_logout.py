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


def test_logout(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    init_callback_mock = mocker.patch("argilla_v1.cli.callback.init_callback")
    argilla_credentials_remove_mock = mocker.patch("argilla_v1.client.login.ArgillaCredentials.remove")

    result = cli_runner.invoke(
        cli,
        "logout",
    )
    assert result.exit_code == 0

    init_callback_mock.assert_called_once()
    argilla_credentials_remove_mock.assert_called_once()


def test_logout_fails(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    init_callback_mock = mocker.patch("argilla_v1.cli.callback.init_callback")
    init_callback_mock.side_effect = ValueError("Error")

    result = cli_runner.invoke(
        cli,
        "logout",
    )
    assert result.exit_code == 1

    init_callback_mock.assert_called_once()
