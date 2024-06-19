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
from typing import TYPE_CHECKING
from uuid import uuid4

import httpx
import pytest
from argilla_v1.cli.app import app
from argilla_v1.client.sdk.users.models import UserRole
from argilla_v1.client.sdk.v1.workspaces.models import WorkspaceModel
from argilla_v1.client.users import User
from argilla_v1.client.workspaces import Workspace
from typer.testing import CliRunner

if TYPE_CHECKING:
    from argilla_v1.cli.typer_ext import ArgillaTyper
    from pytest_mock import MockerFixture


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def cli() -> "ArgillaTyper":
    return app


@pytest.fixture
def login_mock(mocker: "MockerFixture") -> None:
    mocker.patch("argilla_v1.client.login.ArgillaCredentials.exists", return_value=True)
    mocker.patch("argilla_v1.client.api.ArgillaSingleton.init")


@pytest.fixture
def not_logged_mock(mocker: "MockerFixture") -> None:
    mocker.patch("argilla_v1.client.login.ArgillaCredentials.exists", return_value=False)


@pytest.fixture
def workspace() -> Workspace:
    workspace = Workspace.__new__(Workspace)
    workspace.__dict__.update(
        {
            "id": uuid4(),
            "name": "unit-test",
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )
    return workspace


@pytest.fixture
def user(mocker: "MockerFixture", workspace: Workspace) -> User:
    mocker.patch.object(
        User,
        "workspaces",
        new_callable=lambda: [
            WorkspaceModel(
                id=workspace.id, name=workspace.name, inserted_at=workspace.inserted_at, updated_at=workspace.updated_at
            )
        ],
    )
    user = User.__new__(User)
    user.__dict__.update(
        {
            "_client": httpx.Client(),
            "id": uuid4(),
            "username": "unit-test",
            "last_name": "unit-test",
            "first_name": "unit-test",
            "role": UserRole.admin,
            "api_key": "apikey.unit-test",
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )
    return user
