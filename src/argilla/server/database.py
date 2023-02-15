from sqlalchemy import create_engine, Table, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///argilla.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# TODO: Maybe we should save this as a variable and used it on users and workspace models
# instead of a string.
Table(
    "users_workspaces",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("workspace_id", ForeignKey("workspaces.id"), primary_key=True),
)
