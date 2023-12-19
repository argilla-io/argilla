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
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint, and_, sql
from sqlalchemy import Enum as SAEnum
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from argilla.server.enums import (
    DatasetStatus,
    MetadataPropertyType,
    QuestionType,
    ResponseStatus,
    SuggestionType,
    UserRole,
)
from argilla.server.models.base import DatabaseModel
from argilla.server.models.metadata_properties import MetadataPropertySettings
from argilla.server.models.mixins import inserted_at_current_value
from argilla.server.models.questions import QuestionSettings

# Include here the data model ref to be accessible for automatic alembic migration scripts
__all__ = [
    "Dataset",
    "Field",
    "Question",
    "Record",
    "Response",
    "Suggestion",
    "User",
    "Workspace",
    "WorkspaceUser",
    "MetadataProperty",
    "Vector",
    "VectorSettings",
]

_USER_API_KEY_BYTES_LENGTH = 80


class Field(DatabaseModel):
    __tablename__ = "fields"

    name: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(Text)
    required: Mapped[bool] = mapped_column(default=False)
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), default={})
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="fields")

    __table_args__ = (UniqueConstraint("name", "dataset_id", name="field_name_dataset_id_uq"),)

    def __repr__(self):
        return (
            f"Field(id={str(self.id)!r}, name={self.name!r}, required={self.required!r}, "
            f"dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


ResponseStatusEnum = SAEnum(ResponseStatus, name="response_status_enum")


class Response(DatabaseModel):
    __tablename__ = "responses"

    values: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSON))
    status: Mapped[ResponseStatus] = mapped_column(ResponseStatusEnum, default=ResponseStatus.submitted, index=True)
    record_id: Mapped[UUID] = mapped_column(ForeignKey("records.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

    record: Mapped["Record"] = relationship(back_populates="responses")
    user: Mapped["User"] = relationship(back_populates="responses")

    __table_args__ = (UniqueConstraint("record_id", "user_id", name="response_record_id_user_id_uq"),)
    __upsertable_columns__ = {"values", "status"}

    @property
    def is_submitted(self):
        return self.status == ResponseStatus.submitted

    def __repr__(self):
        return (
            f"Response(id={str(self.id)!r}, record_id={str(self.record_id)!r}, user_id={str(self.user_id)!r}, "
            f"status={self.status.value!r}, inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


SuggestionTypeEnum = SAEnum(SuggestionType, name="suggestion_type_enum")


class Suggestion(DatabaseModel):
    __tablename__ = "suggestions"

    value: Mapped[Any] = mapped_column(JSON)
    score: Mapped[Optional[float]] = mapped_column(nullable=True)
    agent: Mapped[Optional[str]] = mapped_column(nullable=True)
    type: Mapped[Optional[SuggestionType]] = mapped_column(SuggestionTypeEnum, nullable=True, index=True)
    record_id: Mapped[UUID] = mapped_column(ForeignKey("records.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)

    record: Mapped["Record"] = relationship(back_populates="suggestions")
    question: Mapped["Question"] = relationship(back_populates="suggestions")

    __table_args__ = (UniqueConstraint("record_id", "question_id", name="suggestion_record_id_question_id_uq"),)
    __upsertable_columns__ = {"value", "score", "agent", "type"}

    def __repr__(self) -> str:
        return (
            f"Suggestion(id={self.id}, score={self.score}, agent={self.agent}, type={self.type}, "
            f"record_id={self.record_id}, question_id={self.question_id}, inserted_at={self.inserted_at}, "
            f"updated_at={self.updated_at})"
        )


class Vector(DatabaseModel):
    __tablename__ = "vectors"

    value: Mapped[List[Any]] = mapped_column(JSON)
    record_id: Mapped[UUID] = mapped_column(ForeignKey("records.id", ondelete="CASCADE"), index=True)
    vector_settings_id: Mapped[UUID] = mapped_column(ForeignKey("vectors_settings.id", ondelete="CASCADE"), index=True)

    record: Mapped["Record"] = relationship(back_populates="vectors")
    vector_settings: Mapped["VectorSettings"] = relationship(back_populates="vectors")

    __table_args__ = (
        UniqueConstraint("record_id", "vector_settings_id", name="vector_record_id_vector_settings_id_uq"),
    )
    __upsertable_columns__ = {"value"}

    def __repr__(self) -> str:
        return (
            f"Vector(id={self.id}, vector_settings_id={self.vector_settings_id}, record_id={self.record_id}, "
            f"inserted_at={self.inserted_at}, updated_at={self.updated_at})"
        )


class VectorSettings(DatabaseModel):
    __tablename__ = "vectors_settings"

    name: Mapped[str] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(Text)
    dimensions: Mapped[int] = mapped_column()
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="vectors_settings")
    vectors: Mapped[List["Vector"]] = relationship(
        back_populates="vector_settings",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Vector.inserted_at.asc(),
    )

    __table_args__ = (UniqueConstraint("name", "dataset_id", name="vector_settings_name_dataset_id_uq"),)

    def __repr__(self) -> str:
        return (
            f"VectorSettings(id={self.id}, name={self.name}, dimensions={self.dimensions}, "
            f"dataset_id={self.dataset_id}, inserted_at={self.inserted_at}, updated_at={self.updated_at})"
        )


class Record(DatabaseModel):
    __tablename__ = "records"

    fields: Mapped[dict] = mapped_column(JSON, default={})
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", MutableDict.as_mutable(JSON), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(index=True)
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="records")
    responses: Mapped[List["Response"]] = relationship(
        back_populates="record",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Response.inserted_at.asc(),
    )
    suggestions: Mapped[List["Suggestion"]] = relationship(
        back_populates="record",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Suggestion.inserted_at.asc(),
    )
    vectors: Mapped[List["Vector"]] = relationship(
        back_populates="record",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Vector.inserted_at.asc(),
    )

    __table_args__ = (UniqueConstraint("external_id", "dataset_id", name="record_external_id_dataset_id_uq"),)

    def __repr__(self):
        return (
            f"Record(id={str(self.id)!r}, external_id={self.external_id!r}, dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )

    def vector_value_by_vector_settings(self, vector_settings: "VectorSettings") -> Union[List[float], None]:
        for vector in self.vectors:
            if vector.vector_settings_id == vector_settings.id:
                return vector.value


class Question(DatabaseModel):
    __tablename__ = "questions"

    name: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    required: Mapped[bool] = mapped_column(default=False)
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), default={})
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="questions")
    suggestions: Mapped[List["Suggestion"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Suggestion.inserted_at.asc(),
    )

    __table_args__ = (UniqueConstraint("name", "dataset_id", name="question_name_dataset_id_uq"),)

    @property
    def parsed_settings(self) -> QuestionSettings:
        return parse_obj_as(QuestionSettings, self.settings)

    @property
    def type(self) -> QuestionType:
        return QuestionType(self.settings["type"])

    def __repr__(self):
        return (
            f"Question(id={str(self.id)!r}, name={self.name!r}, required={self.required!r}, "
            f"dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class MetadataProperty(DatabaseModel):
    __tablename__ = "metadata_properties"

    name: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(Text)
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), default={})
    allowed_roles: Mapped[List[UserRole]] = mapped_column(MutableList.as_mutable(JSON), default=[], server_default="[]")
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="metadata_properties")

    __table_args__ = (UniqueConstraint("name", "dataset_id", name="metadata_property_name_dataset_id_uq"),)

    @property
    def type(self) -> MetadataPropertyType:
        return MetadataPropertyType(self.settings["type"])

    @property
    def parsed_settings(self) -> MetadataPropertySettings:
        return parse_obj_as(MetadataPropertySettings, self.settings)

    @property
    def visible_for_annotators(self) -> bool:
        return UserRole.annotator in self.allowed_roles

    def __repr__(self):
        return (
            f"MetadataProperty(id={str(self.id)!r}, name={self.name!r}, dataset_id={str(self.dataset_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


DatasetStatusEnum = SAEnum(DatasetStatus, name="dataset_status_enum")


def _updated_at_current_value(context: DefaultExecutionContext) -> datetime:
    return context.get_current_parameters(isolate_multiinsert_groups=False)["updated_at"]


class Dataset(DatabaseModel):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(index=True)
    guidelines: Mapped[Optional[str]] = mapped_column(Text)
    allow_extra_metadata: Mapped[bool] = mapped_column(default=True, server_default=sql.true())
    status: Mapped[DatasetStatus] = mapped_column(DatasetStatusEnum, default=DatasetStatus.draft, index=True)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=inserted_at_current_value, onupdate=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(
        default=inserted_at_current_value, onupdate=_updated_at_current_value
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="datasets")
    fields: Mapped[List["Field"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Field.inserted_at.asc(),
    )
    questions: Mapped[List["Question"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Question.inserted_at.asc(),
    )
    records: Mapped[List["Record"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=Record.inserted_at.asc(),
    )
    metadata_properties: Mapped[List["MetadataProperty"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=MetadataProperty.inserted_at.asc(),
    )
    vectors_settings: Mapped[List["VectorSettings"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=VectorSettings.inserted_at.asc(),
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
            f"last_activity_at={str(self.last_activity_at)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class WorkspaceUser(DatabaseModel):
    __tablename__ = "workspaces_users"

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    workspace: Mapped["Workspace"] = relationship(viewonly=True)
    user: Mapped["User"] = relationship(viewonly=True)

    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="workspace_id_user_id_uq"),)

    def __repr__(self):
        return (
            f"WorkspaceUser(id={str(self.id)!r}, workspace_id={str(self.workspace_id)!r}, "
            f"user_id={str(self.user_id)!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


class Workspace(DatabaseModel):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(unique=True, index=True)

    datasets: Mapped[List["Dataset"]] = relationship(back_populates="workspace", order_by=Dataset.inserted_at.asc())
    users: Mapped[List["User"]] = relationship(
        secondary="workspaces_users", back_populates="workspaces", order_by=WorkspaceUser.inserted_at.asc()
    )

    def __repr__(self):
        return (
            f"Workspace(id={str(self.id)!r}, name={self.name!r}, "
            f"inserted_at={str(self.inserted_at)!r}, updated_at={str(self.updated_at)!r})"
        )


def generate_user_api_key() -> str:
    return secrets.token_urlsafe(_USER_API_KEY_BYTES_LENGTH)


UserRoleEnum = SAEnum(UserRole, name="user_role_enum")


class User(DatabaseModel):
    __tablename__ = "users"

    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    username: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(UserRoleEnum, default=UserRole.annotator, index=True)
    api_key: Mapped[str] = mapped_column(Text, unique=True, index=True, default=generate_user_api_key)
    password_hash: Mapped[str] = mapped_column(Text)

    workspaces: Mapped[List["Workspace"]] = relationship(
        secondary="workspaces_users", back_populates="users", order_by=WorkspaceUser.inserted_at.asc()
    )
    responses: Mapped[List["Response"]] = relationship(back_populates="user")
    datasets: Mapped[List["Dataset"]] = relationship(
        secondary="workspaces_users",
        primaryjoin="User.id == WorkspaceUser.user_id",
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
