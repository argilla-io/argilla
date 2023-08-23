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

import pytest

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer
    from argilla.server.models import User as ServerUser

# from tests.integration.conftest import owner
from tests.integration.conftest import *  # for owner fixture
from argilla.client.workspaces import Workspace
from argilla.tasks.workspaces.list import list_workspaces

from argilla.client.sdk.users.models import UserRole

from argilla.client.api import ArgillaSingleton
from tests.factories import (
    UserFactory,
    WorkspaceFactory,
)


@pytest.mark.asyncio
async def test_list_workspaces(mocker: "MockerFixture", capsys):
    ws_factory = await WorkspaceFactory.create(name="test_workspace")

    workspace_list_mock = mocker.patch("argilla.client.workspaces.Workspace.list")
    workspace_list_mock.return_value = [ws_factory]
    list_workspaces()
    captured = capsys.readouterr()
    assert all(col in captured.out for col in ("ID", "Name", "Creation Date", "Update Date", "test_workspace"))


@pytest.mark.asyncio
async def test_cli_workspaces_list(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture", owner: "ServerUser"):
    ws_factory = await WorkspaceFactory.create(name="test_workspace")
    mocker.patch("argilla.client.api.ArgillaSingleton.init")
    
    workspace_list_mock = mocker.patch("argilla.client.workspaces.Workspace.list")
    workspace_list_mock.return_value = [ws_factory]

    result = cli_runner.invoke(
        cli,
        "workspaces list",
    )

    assert all(col in result.stdout for col in ("ID", "Name", "Creation Date", "Update Date", "test_workspace"))
    assert result.exit_code == 0
