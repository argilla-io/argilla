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
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import parse_obj_as
from sqlalchemy import JSON, ForeignKey, Index, Text, UniqueConstraint, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from argilla.server.database import Base
from argilla.server.models import QuestionSettings

_USER_API_KEY_BYTES_LENGTH = 80


def generate_user_api_key():
    return secrets.token_urlsafe(_USER_API_KEY_BYTES_LENGTH)


def default_inserted_at(context):
    return context.get_current_parameters()["inserted_at"]


class FieldType(str, Enum):
    text = "text"


class ResponseStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"


class DatasetStatus(str, Enum):
    draft = "draft"
    ready = "ready"


class UserRole(str, Enum):
    owner = "owner"
    admin = "admin"
    annotator = "annotator"


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, index=True)
    title: Mapped[str] = mapped_column(Text)
    required: Mapped[bool] = mapped_column(default=False)
    settings: Mapped[dict] = mapped_column(JSON, default={})
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="fields")

    __table_args__ = (UniqueConstraint("name", "dataset_id", name="field_name_dataset_id_uq"),)

    def __repr__(self):
        return (
            f"Field(id={str(self.id)!r}, name={self.name!r}, required={self.required!r}, "
            f"dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    values: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[ResponseStatus] = mapped_column(default=ResponseStatus.submitted, index=True)
    record_id: Mapped[UUID] = mapped_column(ForeignKey("records.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    record: Mapped["Record"] = relationship(back_populates="responses")
    user: Mapped["User"] = relationship(back_populates="responses")

    __table_args__ = (UniqueConstraint("record_id", "user_id", name="response_record_id_user_id_uq"),)

    @property
    def is_submitted(self):
        return self.status == ResponseStatus.submitted

    def __repr__(self):
        return (
            f"Response(id={str(self.id)!r}, record_id={str(self.record_id)!r}, user_id={str(self.user_id)!r}, "
            f"status={self.status.value!r}, inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class Record(Base):
    __tablename__ = "records"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    fields: Mapped[dict] = mapped_column(JSON, default={})
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(index=True)
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="records")
    responses: Mapped[List["Response"]] = relationship(back_populates="record", order_by=Response.inserted_at.asc())

    __table_args__ = (UniqueConstraint("external_id", "dataset_id", name="record_external_id_dataset_id_uq"),)

    def __repr__(self):
        return (
            f"Record(id={str(self.id)!r}, external_id={self.external_id!r}, dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    required: Mapped[bool] = mapped_column(default=False)
    settings: Mapped[dict] = mapped_column(JSON, default={})
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="questions")

    __table_args__ = (UniqueConstraint("name", "dataset_id", name="question_name_dataset_id_uq"),)

    @property
    def parsed_settings(self) -> QuestionSettings:
        return parse_obj_as(QuestionSettings, self.settings)

    def __repr__(self):
        return (
            f"Question(id={str(self.id)!r}, name={self.name!r}, required={self.required!r}, "
            f"dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(index=True)
    guidelines: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[DatasetStatus] = mapped_column(default=DatasetStatus.draft, index=True)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship(back_populates="datasets")
    fields: Mapped[List["Field"]] = relationship(
        back_populates="dataset", passive_deletes=True, order_by=Field.inserted_at.asc()
    )
    questions: Mapped[List["Question"]] = relationship(
        back_populates="dataset", passive_deletes=True, order_by=Question.inserted_at.asc()
    )
    records: Mapped[List["Record"]] = relationship(
        back_populates="dataset", passive_deletes=True, order_by=Record.inserted_at.asc()
    )

    __table_args__ = (UniqueConstraint("name", "workspace_id", name="dataset_name_workspace_id_uq"),)

    @property
    def is_draft(self):
        return self.status == DatasetStatus.draft

    @property
    def is_ready(self):
        return self.status == DatasetStatus.ready

    def __repr__(self):
        return (
            f"Dataset(id={str(self.id)!r}, name={self.name!r}, guidelines={self.guidelines!r}, "
            f"status={self.status.value!r}, workspace_id={str(self.workspace_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class WorkspaceUser(Base):
    __tablename__ = "workspaces_users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship(viewonly=True)
    user: Mapped["User"] = relationship(viewonly=True)

    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="workspace_id_user_id_uq"),)

    def __repr__(self):
        return (
            f"WorkspaceUser(id={str(self.id)!r}, workspace_id={str(self.workspace_id)!r}, "
            f"user_id={str(self.user_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(unique=True, index=True)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    datasets: Mapped[List["Dataset"]] = relationship(back_populates="workspace", order_by=Dataset.inserted_at.asc())
    users: Mapped[List["User"]] = relationship(
        secondary="workspaces_users", back_populates="workspaces", order_by=WorkspaceUser.inserted_at.asc()
    )

    def __repr__(self):
        return (
            f"Workspace(id={str(self.id)!r}, name={self.name!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    username: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.annotator, index=True)
    api_key: Mapped[str] = mapped_column(Text, unique=True, index=True, default=generate_user_api_key)
    password_hash: Mapped[str] = mapped_column(Text)

    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=default_inserted_at, onupdate=datetime.utcnow)

    workspaces: Mapped[List["Workspace"]] = relationship(
        secondary="workspaces_users", back_populates="users", order_by=WorkspaceUser.inserted_at.asc()
    )
    responses: Mapped[List["Response"]] = relationship(back_populates="user")
    datasets: Mapped[List["Dataset"]] = relationship(
        secondary="workspaces_users",
        primaryjoin=id == WorkspaceUser.user_id,
        secondaryjoin=and_(
            Workspace.id == Dataset.workspace_id,
            WorkspaceUser.workspace_id == Workspace.id,
        ),
        viewonly=True,
        order_by=Dataset.inserted_at.asc(),
    )

    @property
    def is_owner(self):
        return self.role == UserRole.owner

    @property
    def is_admin(self):
        return self.role == UserRole.admin

    @property
    def is_annotator(self):
        return self.role == UserRole.annotator

    def __repr__(self):
        return (
            f"User(id={str(self.id)!r}, first_name={self.first_name!r}, last_name={self.last_name!r}, "
            f"username={self.username!r}, role={self.role.value!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )
