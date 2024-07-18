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
from argilla_server.contexts import accounts
from argilla_server.models import User, UserRole, Workspace
from click.testing import CliRunner
from typer import Typer

from tests.factories import UserSyncFactory, WorkspaceSyncFactory

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@pytest.mark.parametrize("role_string", ["owner", "admin", "annotator"])
def test_create(sync_db: "Session", cli_runner: CliRunner, cli: Typer, role_string: str):
    result = cli_runner.invoke(
        cli,
        f"database users create --first-name first-name --username username --role {role_string} "
        "--password 12345678 --workspace workspace",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 1

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert user.first_name == "first-name"
    assert user.username == "username"
    assert user.role.value == UserRole(role_string).value
    assert accounts.verify_password("12345678", user.password_hash)
    assert user.api_key
    assert [ws.name for ws in user.workspaces] == ["workspace"]


def test_create_with_default_role(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --password 12345678",
        input="\n",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert user.role == UserRole.annotator


@pytest.mark.parametrize("role_string", ["owner", "admin", "annotator"])
def test_create_with_input_role(sync_db: "Session", cli_runner: CliRunner, cli: Typer, role_string: str):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --password 12345678",
        input=f"{role_string}\n",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert user.role.value == UserRole(role_string).value


def test_create_with_invalid_role(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role bad_role "
        "--password 12345678 --workspace workspace",
    )

    assert result.exit_code == 2
    assert sync_db.query(User).count() == 0
    assert sync_db.query(Workspace).count() == 0


def test_create_with_input_password(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role owner",
        input="12345678\n12345678\n",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert accounts.verify_password("12345678", user.password_hash)


def test_create_with_invalid_password(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli, "database users create --first-name first-name --username username --password 1234 --role owner"
    )

    assert result.exit_code == 1
    assert sync_db.query(User).count() == 0
    assert sync_db.query(Workspace).count() == 0


def test_create_with_input_username(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli, "database users create --first-name first-name --password 12345678", input="username\n"
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0

    assert sync_db.query(User).filter_by(username="username").first()


def test_create_with_invalid_username(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username -Invalid-Username --password 12345678 --role owner",
    )

    assert result.exit_code == 1
    assert sync_db.query(User).count() == 0
    assert sync_db.query(Workspace).count() == 0


def test_create_with_existing_username(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    UserSyncFactory.create(username="username")

    result = cli_runner.invoke(
        cli, "database users create --first-name first-name --username username --role owner --password 12345678"
    )

    assert result.exit_code == 0
    assert "username" in result.output
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0


def test_create_with_last_name(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --last-name last-name --username username --password 12345678 --role owner",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert user.last_name == "last-name"


def test_create_with_api_key(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role owner --password 12345678 --api-key abcdefgh",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert user.api_key == "abcdefgh"


def test_create_with_invalid_api_key(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role owner --password 12345678 --api-key abc",
    )

    assert result.exit_code == 1
    assert sync_db.query(User).count() == 0
    assert sync_db.query(Workspace).count() == 0


def test_create_with_existing_api_key(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    UserSyncFactory.create(api_key="abcdefgh")

    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role owner --password 12345678 --api-key abcdefgh",
    )

    assert result.exit_code == 0
    assert "abcdefgh" in result.output
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 0


def test_create_with_multiple_workspaces(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role owner --password 12345678 "
        "--workspace workspace-a --workspace workspace-b",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 2

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert [ws.name for ws in user.workspaces] == ["workspace-a", "workspace-b"]


def test_create_with_existent_workspaces(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    WorkspaceSyncFactory.create(name="workspace-a")
    WorkspaceSyncFactory.create(name="workspace-b")

    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role owner --password 12345678 "
        "--workspace workspace-a --workspace workspace-b --workspace workspace-c",
    )

    assert result.exit_code == 0
    assert sync_db.query(User).count() == 1
    assert sync_db.query(Workspace).count() == 3

    user = sync_db.query(User).filter_by(username="username").first()
    assert user
    assert [ws.name for ws in user.workspaces] == ["workspace-a", "workspace-b", "workspace-c"]


def test_create_with_invalid_workspaces(sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "database users create --first-name first-name --username username --role owner --password 12345678 "
        "--workspace workspace-a --workspace 'invalid workspace' --workspace workspace-c",
    )

    assert result.exit_code == 1
    assert sync_db.query(User).count() == 0
    assert sync_db.query(Workspace).count() == 0
