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

import os
from typing import TYPE_CHECKING
from unittest import mock

from argilla_server.models import User, UserRole, Workspace, WorkspaceUser
from click.testing import CliRunner
from typer import Typer

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def test_migrate(monkeypatch, sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    mock_users_file = os.path.join(os.path.dirname(__file__), "test_user_files", "users.yml")

    with mock.patch.dict(os.environ, {"ARGILLA_LOCAL_AUTH_USERS_DB_FILE": mock_users_file}):
        result = cli_runner.invoke(cli, "database users migrate")

        assert result.exit_code == 0
        assert sync_db.query(User).count() == 5
        assert sync_db.query(Workspace).count() == 9
        assert sync_db.query(WorkspaceUser).count() == 11

        user = sync_db.query(User).filter_by(username="john").first()
        assert user.first_name == "John Doe"
        assert user.username == "john"
        assert user.role == UserRole.owner
        assert user.api_key == "a14427ea-9197-11ec-b909-0242ac120002"
        assert user.password_hash == "$2y$05$xtl7iy3bpqchUwiQMjEHe.tY7OaIjDrg43W3TB4EHQ7izvdjvGtPS"
        assert [ws.name for ws in user.workspaces] == ["john"]

        user = sync_db.query(User).filter_by(username="tanya").first()
        assert user.first_name == "Tanya Franklin"
        assert user.username == "tanya"
        assert user.role == UserRole.annotator
        assert user.api_key == "78a10b53-8db7-4ab5-9e9e-fbd4b7e76551"
        assert user.password_hash == "$2y$05$aqNyXcXRXddNj5toZwT0HugHqKZypvqlBAkZviAGGbsAC8oTj/P5K"
        assert [ws.name for ws in user.workspaces] == ["tanya", "argilla", "team"]

        user = sync_db.query(User).filter_by(username="daisy").first()
        assert user.first_name == "Daisy Gonzalez"
        assert user.username == "daisy"
        assert user.role == UserRole.annotator
        assert user.api_key == "a8168929-8668-494c-b7a5-98cd35740d9b"
        assert user.password_hash == "$2y$05$l83IhUs4ZDaxsgZ/P12FO.RFTi2wKQ2AxMK2vYtLx//yKramuCcZG"
        assert set([ws.name for ws in user.workspaces]) == {"daisy", "argilla", "team", "latam"}

        user = sync_db.query(User).filter_by(username="macleod").first()
        assert user.first_name == ""
        assert user.username == "macleod"
        assert user.role == UserRole.annotator
        assert user.api_key == "7c3b4d6e-1898-4c42-84c8-e1758cea1ce0"
        assert user.password_hash == "$2y$05$Fb3iv7AGv8k.o5cl9qdCtuwkrLcDcSYKWyJk1QNl6RXKUecvP.Ium"
        assert [ws.name for ws in user.workspaces] == ["macleod", "highlands"]

        user = sync_db.query(User).filter_by(username="sanchez").first()
        assert user.first_name == "Juan Sánchez Villalobos Ramírez"
        assert user.username == "sanchez"
        assert user.role == UserRole.annotator
        assert user.api_key == "ac7b6b86-7d63-45ce-a76a-08f64e0d5fd6"
        assert user.password_hash == "$2y$05$wMvfoz2TwrRFRZhNELHjbOcqEucVYImNORuRvh7Vp26.dIqvo9tY2"
        assert [ws.name for ws in user.workspaces] == ["sanchez"]


def test_migrate_with_one_user_file(monkeypatch, sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    mock_users_file = os.path.join(os.path.dirname(__file__), "test_user_files", "users_one.yml")

    with mock.patch.dict(os.environ, {"ARGILLA_LOCAL_AUTH_USERS_DB_FILE": mock_users_file}):
        result = cli_runner.invoke(cli, "database users migrate")

        assert result.exit_code == 0
        assert sync_db.query(User).count() == 1
        assert sync_db.query(Workspace).count() == 3
        assert sync_db.query(WorkspaceUser).count() == 3

        user = sync_db.query(User).filter_by(username="john").first()
        assert user.first_name == "John Doe"
        assert user.username == "john"
        assert user.role == UserRole.annotator
        assert user.api_key == "a14427ea-9197-11ec-b909-0242ac120002"
        assert user.password_hash == "$2y$05$xtl7iy3bpqchUwiQMjEHe.tY7OaIjDrg43W3TB4EHQ7izvdjvGtPS"
        assert [ws.name for ws in user.workspaces] == ["john", "argilla", "team"]


def test_migrate_with_nonexistent_file(monkeypatch, sync_db: "Session", cli_runner: CliRunner, cli: Typer):
    with mock.patch.dict(os.environ, {"ARGILLA_LOCAL_AUTH_USERS_DB_FILE": "nonexistent.yml"}):
        result = cli_runner.invoke(cli, "database users migrate")

        assert result.exit_code == 1
        assert sync_db.query(User).count() == 0
        assert sync_db.query(Workspace).count() == 0
        assert sync_db.query(WorkspaceUser).count() == 0
