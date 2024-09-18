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

"""create fields table

Revision ID: ae5522b4c674
Revises: e402e9d9245e
Create Date: 2023-04-21 16:10:27.320399

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = "ae5522b4c674"
down_revision = "e402e9d9245e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fields",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("name", sa.String, nullable=False, index=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("required", sa.Boolean, nullable=False, server_default=expression.false()),
        sa.Column("settings", sa.JSON, nullable=False),
        sa.Column("dataset_id", sa.Uuid, sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("inserted_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("name", "dataset_id", name="field_name_dataset_id_uq"),
    )


def downgrade() -> None:
    op.drop_table("fields")
