#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""create workspaces_users table

Revision ID: 1769ee58fbb4
Revises: 82a5a88a3fa5
Create Date: 2023-02-14 10:36:56.313539

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1769ee58fbb4"
down_revision = "82a5a88a3fa5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workspaces_users",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column(
            "workspace_id", sa.Uuid, sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
        ),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("inserted_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("workspace_id", "user_id", name="workspace_id_user_id_uq"),
    )


def downgrade() -> None:
    op.drop_table("workspaces_users")
