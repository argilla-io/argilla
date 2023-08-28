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
    from pytest_mock import MockerFixture
    from typer import Typer

from tests.factories import WorkspaceSyncFactory


@pytest.mark.usefixtures("login_mock")
def test_cli_workspaces_list(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    ws_factory = WorkspaceSyncFactory.create(name="test_workspace")

    workspace_list_mock = mocker.patch("argilla.client.workspaces.Workspace.list")
    workspace_list_mock.return_value = [ws_factory]

    result = cli_runner.invoke(cli, "workspaces list")

    assert all(col in result.stdout for col in ("ID", "Name", "Creation Date", "Update Date", "test_workspace"))
    assert result.exit_code == 0


def test_cli_workspaces_list_needs_login(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    result = cli_runner.invoke(cli, "workspaces list")

    assert "You are not logged in. Please run `argilla login` to login to an Argilla server." in result.stdout
    assert result.exit_code == 1
