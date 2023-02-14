"""create users_organizations table

Revision ID: 06100f82589e
Revises: 82a5a88a3fa5
Create Date: 2023-02-13 18:22:10.249790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06100f82589e'
down_revision = '82a5a88a3fa5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users_organizations",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("organization_id", sa.Uuid, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("role", sa.String, nullable=False)
    )


def downgrade() -> None:
    op.drop_table("users_organizations")
