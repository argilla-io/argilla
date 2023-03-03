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
from typing import List, Optional

import yaml
from pydantic import BaseModel, constr
from rich import print
from sqlalchemy.orm import Session

from argilla.server.database import SessionLocal
from argilla.server.models import User, Workspace
from argilla.server.security.model import USER_USERNAME_REGEX, WORKSPACE_NAME_REGEX


class WorkspaceCreate(BaseModel):
    name: constr(regex=WORKSPACE_NAME_REGEX, min_length=1)


class UserCreate(BaseModel):
    first_name: constr(strip_whitespace=True)
    username: constr(regex=USER_USERNAME_REGEX, min_length=1)
    api_key: constr(min_length=1)
    password_hash: constr(min_length=1)
    workspaces: Optional[List[WorkspaceCreate]]


class UsersMigrator:
    def __init__(self, users_filename: str):
        self._users_filename = users_filename

        try:
            with open(users_filename) as users_file:
                self._users = yaml.safe_load(users_file.read())
        except FileNotFoundError:
            self._users = []

    def migrate(self):
        print(f"Starting users migration process using file {self._users_filename!r}")

        with SessionLocal() as session, session.begin():
            for user in self._users:
                self._migrate_user(session, user)

            print(f"Users migration process successfully finished")

    def _migrate_user(self, session: Session, user: dict):
        print(f"Migrating User with username {user['username']!r}")

        user_create = self._build_user_create(user)

        session.add(self._build_user(session, user_create))
        session.flush()

    def _build_user_create(self, user: dict):
        return UserCreate(
            first_name=user.get("full_name", ""),
            username=user["username"],
            api_key=user["api_key"],
            password_hash=user["hashed_password"],
            workspaces=[WorkspaceCreate(name=name) for name in user.get("workspaces", [])],
        )

    def _build_user(self, session: Session, user_create: UserCreate):
        return User(
            first_name=user_create.first_name,
            username=user_create.username,
            api_key=user_create.api_key,
            password_hash=user_create.password_hash,
            workspaces=[self._get_or_new_workspace(session, workspace.name) for workspace in user_create.workspaces],
        )

    def _get_or_new_workspace(self, session: Session, workspace_name: str):
        return session.query(Workspace).filter_by(name=workspace_name).first() or Workspace(name=workspace_name)


if __name__ == "__main__":
    UsersMigrator(os.environ["ARGILLA_LOCAL_AUTH_USERS_DB_FILE"]).migrate()
