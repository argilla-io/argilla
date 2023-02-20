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

import secrets
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from argilla.server.database import Base

_USER_API_KEY_BYTES_LENGTH = 80


def generate_user_api_key():
    return secrets.token_urlsafe(_USER_API_KEY_BYTES_LENGTH)


class UserWorkspace(Base):
    __tablename__ = "users_workspaces"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"))


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]

    users: Mapped[List["User"]] = relationship(secondary="users_workspaces", back_populates="workspaces")


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    username: Mapped[str]
    api_key: Mapped[str] = mapped_column(Text, unique=True, default=generate_user_api_key)
    password_hash: Mapped[str] = mapped_column(Text)

    workspaces: Mapped[List["Workspace"]] = relationship(secondary="users_workspaces", back_populates="users")
