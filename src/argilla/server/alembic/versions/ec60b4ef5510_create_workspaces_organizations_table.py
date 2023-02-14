"""create workspaces_organizations table

Revision ID: ec60b4ef5510
Revises: 1769ee58fbb4
Create Date: 2023-02-14 10:42:34.813230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec60b4ef5510'
down_revision = '1769ee58fbb4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workspaces_organizations",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("workspace_id", sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False, unique=True),
        sa.Column("organization_id", sa.Uuid, sa.ForeignKey("organizations.id"), nullable=False)
    )


def downgrade() -> None:
    op.drop_table("workspaces_organizations")
