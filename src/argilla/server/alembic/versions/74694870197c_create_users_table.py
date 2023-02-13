"""create users table

Revision ID: 74694870197c
Revises:
Create Date: 2023-02-13 17:08:05.445314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "74694870197c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("first_name", sa.String),
        sa.Column("last_name", sa.String),
        sa.Column("username", sa.String, nullable=False, unique=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("password_reset_token", sa.Text, unique=True),
        sa.Column("api_key", sa.Text, unique=True)
    )


def downgrade() -> None:
    op.drop_table("users")
