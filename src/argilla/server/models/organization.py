import uuid

from sqlalchemy.orm import Mapped, mapped_column

from argilla.server.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
