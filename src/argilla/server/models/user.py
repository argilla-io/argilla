import uuid
from typing import Optional

from sqlalchemy import String, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from argilla.server.database import Base, SessionLocal


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


session = SessionLocal()

result = session.scalars(
    select(User).where(User.username == "poto")
)

print(list(result))

user = User(username="poto")
session.add(user)
session.commit()