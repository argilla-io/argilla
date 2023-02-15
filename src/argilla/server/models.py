import uuid
from typing import Optional, List

from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from argilla.server.database import Base


class UserWorkspace(Base):
    __tablename__ = "users_workspaces"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"))


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]

    users: Mapped[List["User"]] = relationship(secondary="users_workspaces", back_populates="workspaces")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    username: Mapped[str]
    email: Mapped[str]
    api_key: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    password_reset_token: Mapped[Optional[str]] = mapped_column(Text, unique=True)

    workspaces: Mapped[List["Workspace"]] = relationship(secondary="users_workspaces", back_populates="users")
