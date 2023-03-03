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

import pytest
from argilla.server.models import User, Workspace, WorkspaceUser
from argilla.tasks.users_migrator import UsersMigrator
from pydantic import ValidationError
from sqlalchemy.orm import Session


def test_users_migrator(db: Session):
    UsersMigrator(os.path.join(os.path.dirname(__file__), "test_users.yml")).migrate()

    assert db.query(User).count() == 4
    assert db.query(Workspace).count() == 4
    assert db.query(WorkspaceUser).count() == 6

    user = db.query(User).filter_by(username="john").first()
    assert user.first_name == "John Doe"
    assert user.username == "john"
    assert user.api_key == "a14427ea-9197-11ec-b909-0242ac120002"
    assert user.password_hash == "$2y$05$xtl7iy3bpqchUwiQMjEHe.tY7OaIjDrg43W3TB4EHQ7izvdjvGtPS"
    assert user.workspaces == []

    user = db.query(User).filter_by(username="tanya").first()
    assert user.first_name == "Tanya Franklin"
    assert user.username == "tanya"
    assert user.api_key == "78a10b53-8db7-4ab5-9e9e-fbd4b7e76551"
    assert user.password_hash == "$2y$05$aqNyXcXRXddNj5toZwT0HugHqKZypvqlBAkZviAGGbsAC8oTj/P5K"
    assert [ws.name for ws in user.workspaces] == ["argilla", "team"]

    user = db.query(User).filter_by(username="daisy").first()
    assert user.first_name == "Daisy Gonzalez"
    assert user.username == "daisy"
    assert user.api_key == "a8168929-8668-494c-b7a5-98cd35740d9b"
    assert user.password_hash == "$2y$05$l83IhUs4ZDaxsgZ/P12FO.RFTi2wKQ2AxMK2vYtLx//yKramuCcZG"
    assert [ws.name for ws in user.workspaces] == ["argilla", "team", "latam"]

    user = db.query(User).filter_by(username="macleod").first()
    assert user.first_name == ""
    assert user.username == "macleod"
    assert user.api_key == "7c3b4d6e-1898-4c42-84c8-e1758cea1ce0"
    assert user.password_hash == "$2y$05$Fb3iv7AGv8k.o5cl9qdCtuwkrLcDcSYKWyJk1QNl6RXKUecvP.Ium"
    assert [ws.name for ws in user.workspaces] == ["highlands"]


def test_users_migrator_with_one_user_file(db: Session):
    UsersMigrator(os.path.join(os.path.dirname(__file__), "test_users_one.yml")).migrate()

    assert db.query(User).count() == 1
    assert db.query(Workspace).count() == 2
    assert db.query(WorkspaceUser).count() == 2

    user = db.query(User).filter_by(username="john").first()
    assert user.first_name == "John Doe"
    assert user.username == "john"
    assert user.api_key == "a14427ea-9197-11ec-b909-0242ac120002"
    assert user.password_hash == "$2y$05$xtl7iy3bpqchUwiQMjEHe.tY7OaIjDrg43W3TB4EHQ7izvdjvGtPS"
    assert [ws.name for ws in user.workspaces] == ["argilla", "team"]


def test_users_migrator_with_invalid_user(db: Session):
    with pytest.raises(ValidationError):
        UsersMigrator(os.path.join(os.path.dirname(__file__), "test_users_invalid_user.yml")).migrate()

    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0
    assert db.query(WorkspaceUser).count() == 0


def test_users_migrator_with_invalid_workspace(db: Session):
    with pytest.raises(ValidationError):
        UsersMigrator(os.path.join(os.path.dirname(__file__), "test_users_invalid_workspace.yml")).migrate()

    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0
    assert db.query(WorkspaceUser).count() == 0


def test_users_migrator_with_nonexistent_file(db: Session):
    UsersMigrator("nonexistent.yml").migrate()

    assert db.query(User).count() == 0
    assert db.query(Workspace).count() == 0
    assert db.query(WorkspaceUser).count() == 0
