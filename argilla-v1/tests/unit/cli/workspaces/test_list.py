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

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer

from argilla_v1.client.workspaces import Workspace
from rich.table import Table

from tests.factories import WorkspaceSyncFactory


@pytest.mark.usefixtures("login_mock")
@pytest.mark.skip(reason="Avoid using db factories")
def test_cli_workspaces_list(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"):
    add_row_spy = mocker.spy(Table, "add_row")
    workspace = WorkspaceSyncFactory.create(name="test_workspace")
    workspace_obj = Workspace.__new__(Workspace)
    workspace_obj.__dict__.update(
        {
            "id": workspace.id,
            "name": workspace.name,
            "inserted_at": workspace.inserted_at,
            "updated_at": workspace.updated_at,
        }
    )
    workspace_list_mock = mocker.patch("argilla_v1.client.workspaces.Workspace.list", return_value=[workspace_obj])

    result = cli_runner.invoke(cli, "workspaces list")

    workspace_list_mock.assert_called_once()
    add_row_spy.assert_called_once_with(
        ANY,  # `self` argument
        str(workspace.id),
        workspace.name,
        workspace.inserted_at.isoformat(sep=" "),
        workspace.updated_at.isoformat(sep=" "),
    )
    assert all(col in result.stdout for col in ("ID", "Name", "Creation Date", "Last Update Date", "test_workspace"))
    assert result.exit_code == 0


@pytest.mark.usefixtures("not_logged_mock")
def test_cli_workspaces_list_needs_login(cli_runner: "CliRunner", cli: "Typer"):
    result = cli_runner.invoke(cli, "workspaces list")

    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
    assert result.exit_code == 1
