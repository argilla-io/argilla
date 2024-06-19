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


@pytest.mark.usefixtures("login_mock")
class TestSuiteWorkspaceCreateCommand:
    def test_cli_workspaces_create_without_name(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
        result = cli_runner.invoke(cli, "workspaces create")
        assert result.exit_code == 2

    def test_cli_workspaces_create_with_name(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"
    ) -> None:
        workspaces_create_mock = mocker.patch("argilla_v1.client.workspaces.Workspace.create")
        result = cli_runner.invoke(cli, "workspaces create workspace25")

        assert result.exit_code == 0
        workspaces_create_mock.assert_called_once_with(name="workspace25")

    def test_workspace_create_already_exists(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
        mocker.patch(
            "argilla_v1.client.workspaces.Workspace.create",
            side_effect=ValueError("Workspace with name=`workspace1` already exists, so please use a different name."),
        )

        result = cli_runner.invoke(cli, "workspaces create workspace1")

        assert "Workspace with name=workspace1 already exists" in result.stdout
        assert result.exit_code == 1

    def test_workspace_create_runtime_exception(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
        mocker.patch(
            "argilla_v1.client.workspaces.Workspace.create",
            side_effect=RuntimeError("An unexpected error occurred when trying to create the workspace"),
        )

        result = cli_runner.invoke(cli, "workspaces create workspace1")
        assert "An unexpected error occurred when trying to create the workspace" in result.stdout
        assert result.exit_code == 1


@pytest.mark.usefixtures("not_logged_mock")
def test_cli_workspaces_create_needs_login(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    result = cli_runner.invoke(cli, "workspaces create")

    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
    assert result.exit_code == 1
