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
class TestSuiteWorkspaceDeleteUser:
    def test_workspace_delete_user(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", workspace, user
    ) -> None:
        mocker.patch("argilla_v1.client.workspaces.Workspace.from_name", return_value=workspace)
        mocker.patch("argilla_v1.client.users.User.from_name", return_value=user)
        mocker.patch("argilla_v1.client.workspaces.Workspace.delete_user")

        result = cli_runner.invoke(cli, "workspaces --name unit-test delete-user unit-test")

        assert result.exit_code == 0
        assert "User with username=unit-test has been removed from workspace=unit-test" in result.stdout

    def test_workspace_delete_user_with_non_existing_workspace(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"
    ) -> None:
        mocker.patch("argilla_v1.client.workspaces.Workspace.from_name", side_effect=ValueError)

        result = cli_runner.invoke(cli, "workspaces --name unit-test delete-user unit-test")

        assert result.exit_code == 1
        assert "Workspace with name=unit-test does not exist" in result.stdout

    def test_workspace_delete_user_with_non_existing_user(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", workspace, user
    ) -> None:
        mocker.patch("argilla_v1.client.workspaces.Workspace.from_name", return_value=workspace)
        mocker.patch("argilla_v1.client.users.User.from_name", side_effect=ValueError)

        result = cli_runner.invoke(cli, "workspaces --name unit-test delete-user unit-test")

        assert result.exit_code == 1
        assert "User with username=unit-test does not exist" in result.stdout

    def test_workspace_delete_user_with_owner_user(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", workspace, user
    ) -> None:
        user.role = "owner"
        mocker.patch("argilla_v1.client.workspaces.Workspace.from_name", return_value=workspace)
        mocker.patch("argilla_v1.client.users.User.from_name", return_value=user)

        result = cli_runner.invoke(cli, "workspaces --name unit-test delete-user unit-test")

        assert result.exit_code == 1
        assert "User with username=unit-test is an owner and cannot be removed" in result.stdout

    def test_workspace_delete_user_with_user_not_belonging_to_workspace(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", workspace, user
    ) -> None:
        mocker.patch("argilla_v1.client.workspaces.Workspace.from_name", return_value=workspace)
        mocker.patch("argilla_v1.client.users.User.from_name", return_value=user)
        mocker.patch("argilla_v1.client.workspaces.Workspace.delete_user", side_effect=ValueError)

        result = cli_runner.invoke(cli, "workspaces --name unit-test delete-user unit-test")

        assert result.exit_code == 1
        assert "User with username=unit-test does not belong to the workspace" in result.stdout

    def test_workspace_delete_user_without_workspace_name(self, cli_runner: "CliRunner", cli: "Typer") -> None:
        result = cli_runner.invoke(cli, "workspaces delete-user unit-test")

        assert result.exit_code == 2


@pytest.mark.usefixtures("not_logged_mock")
def test_list_users_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "workspaces --name unit-test delete-user unit-test")

    assert result.exit_code == 1
    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
