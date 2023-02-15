import uuid
from typing import Optional, List

from sqlalchemy import String, Text, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from argilla.server.database import Base


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

    workspaces: Mapped[List["Workspace"]] = relationship(secondary="users_organizations", back_populates="users")


from argilla.server.database import SessionLocal

def seed_database():
    session = SessionLocal()

    session.add_all([
        User(
            first_name="John",
            last_name="Doe",
            username="argilla",
            email="noreply@argilla.io",
            password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
            api_key="1234"
        ),
        User(
            first_name="Luis",
            last_name="Povedano",
            username="pove",
            email="pove@argilla.io",
            password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
            api_key="123456"
        )
    ])

    session.commit()





# result = session.scalars(
#     select(User).where(User.username == "poto")
# )

# print(list(result))

# user = User(username="poto")
# session.add(user)
# session.commit()
