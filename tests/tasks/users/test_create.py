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
from argilla.server.contexts import accounts
from argilla.server.models import User, UserRole, Workspace
from click.testing import CliRunner
from sqlalchemy.orm import Session
from typer import Typer

from tests.factories import UserFactory, WorkspaceFactory


@pytest.mark.parametrize("role_string", ["owner", "admin", "annotator"])
def test_create(db: Session, cli_runner: CliRunner, cli: Typer, role_string: str):
    result = cli_runner.invoke(
        cli,
        f"users create --first-name first-name --username username --role {role_string} "
        "--password 12345678 --workspace workspace",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 1

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert user.first_name == "first-name"
    assert user.username == "username"
    assert user.role.value == UserRole(role_string).value
    assert accounts.verify_password("12345678", user.password_hash)
    assert user.api_key
    assert [ws.name for ws in user.workspaces] == ["workspace"]


def test_create_with_default_role(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --password 12345678",
        input="\n",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert user.role == UserRole.annotator


@pytest.mark.parametrize("role_string", ["owner", "admin", "annotator"])
def test_create_with_input_role(db: Session, cli_runner: CliRunner, cli: Typer, role_string: str):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --password 12345678",
        input=f"{role_string}\n",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert user.role.value == UserRole(role_string).value


def test_create_with_invalid_role(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --role bad_role "
        "--password 12345678 --workspace workspace",
    )

    assert result.exit_code == 2
    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0


def test_create_with_input_password(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --role owner",
        input="12345678\n12345678\n",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert accounts.verify_password("12345678", user.password_hash)


def test_create_with_invalid_password(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli, "users create --first-name first-name --username username --password 1234 --role owner"
    )

    assert result.exit_code == 1
    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0


def test_create_with_input_username(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(cli, "users create --first-name first-name --password 12345678", input="username\n")

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0

    assert db.query(User).filter_by(username="username").first()


def test_create_with_invalid_username(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli, "users create --first-name first-name --username Invalid-Username --password 12345678 --role owner"
    )

    assert result.exit_code == 1
    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0


def test_create_with_existing_username(db: Session, cli_runner: CliRunner, cli: Typer):
    UserFactory.create(username="username")

    result = cli_runner.invoke(
        cli, "users create --first-name first-name --username username --role owner --password 12345678"
    )

    assert result.exit_code == 0
    assert "username" in result.output
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0


def test_create_with_last_name(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --last-name last-name --username username --password 12345678 --role owner",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert user.last_name == "last-name"


def test_create_with_api_key(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --role owner --password 12345678 --api-key abcdefgh",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert user.api_key == "abcdefgh"


def test_create_with_invalid_api_key(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli, "users create --first-name first-name --username username --role owner --password 12345678 --api-key abc"
    )

    assert result.exit_code == 1
    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0


def test_create_with_existing_api_key(db: Session, cli_runner: CliRunner, cli: Typer):
    UserFactory.create(api_key="abcdefgh")

    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --role owner --password 12345678 --api-key abcdefgh",
    )

    assert result.exit_code == 0
    assert "abcdefgh" in result.output
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 0


def test_create_with_multiple_workspaces(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --role owner --password 12345678 "
        "--workspace workspace-a --workspace workspace-b",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 2

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert [ws.name for ws in user.workspaces] == ["workspace-a", "workspace-b"]


def test_create_with_existent_workspaces(db: Session, cli_runner: CliRunner, cli: Typer):
    WorkspaceFactory.create(name="workspace-a")
    WorkspaceFactory.create(name="workspace-b")

    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --role owner --password 12345678 "
        "--workspace workspace-a --workspace workspace-b --workspace workspace-c",
    )

    assert result.exit_code == 0
    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 3

    user = db.query(User).filter_by(username="username").first()
    assert user
    assert [ws.name for ws in user.workspaces] == ["workspace-a", "workspace-b", "workspace-c"]


def test_create_with_invalid_workspaces(db: Session, cli_runner: CliRunner, cli: Typer):
    result = cli_runner.invoke(
        cli,
        "users create --first-name first-name --username username --role owner --password 12345678 "
        "--workspace workspace-a --workspace 'invalid workspace' --workspace workspace-c",
    )

    assert result.exit_code == 1
    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0
