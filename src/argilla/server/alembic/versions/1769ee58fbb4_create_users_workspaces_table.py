"""create users_workspaces table

Revision ID: 1769ee58fbb4
Revises: 06100f82589e
Create Date: 2023-02-14 10:36:56.313539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1769ee58fbb4'
down_revision = '06100f82589e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users_workspaces",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("workspace_id", sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    )


def downgrade() -> None:
    op.drop_table("users_workspaces")
