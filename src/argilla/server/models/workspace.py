import uuid
from typing import List

from sqlalchemy.orm import Mapped, mapped_column,relationship

from argilla.server.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]

    users: Mapped[List["User"]] = relationship(secondary="users_organizations", back_populates="workspaces")
