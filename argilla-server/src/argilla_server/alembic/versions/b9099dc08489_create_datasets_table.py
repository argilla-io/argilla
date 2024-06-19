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

"""create datasets table

Revision ID: b9099dc08489
Revises: 1769ee58fbb4
Create Date: 2023-03-29 17:26:25.432467

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b9099dc08489"
down_revision = "1769ee58fbb4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("name", sa.String, nullable=False, index=True),
        sa.Column("guidelines", sa.Text),
        sa.Column("status", sa.String, nullable=False, index=True),
        sa.Column(
            "workspace_id", sa.Uuid, sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
        ),
        sa.Column("inserted_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("name", "workspace_id", name="dataset_name_workspace_id_uq"),
    )


def downgrade() -> None:
    op.drop_table("datasets")
