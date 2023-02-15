import uuid
from typing import Optional, List

from sqlalchemy import Text, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from argilla.server.database import Base


users_workspaces = Table(
    "users_workspaces",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("workspace_id", ForeignKey("workspaces.id"), primary_key=True),
)


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]

    users: Mapped[List["User"]] = relationship(secondary=users_workspaces, back_populates="workspaces")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    username: Mapped[str]
    email: Mapped[str]
    api_key: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    password_reset_token: Mapped[str] = mapped_column(Text, unique=True)

    workspaces: Mapped[List["Workspace"]] = relationship(secondary=users_workspaces, back_populates="users")
