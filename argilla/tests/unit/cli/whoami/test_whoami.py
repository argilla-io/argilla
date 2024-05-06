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

if TYPE_CHECKING:
    from click.testing import CliRunner
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
def test_cli_whoami(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "whoami")

    assert result.exit_code == 0
    assert "Current User" in result.stdout


@pytest.mark.usefixtures("not_logged_mock")
def test_cli_whoami_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "whoami")

    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
    assert result.exit_code == 1
