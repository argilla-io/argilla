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

"""create records table

Revision ID: 8be56284dac0
Revises: 3a8e2f9b5dea
Create Date: 2023-04-13 12:56:56.456664

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8be56284dac0"
down_revision = "3a8e2f9b5dea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "records",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("fields", sa.JSON, nullable=False),
        sa.Column("external_id", sa.String, index=True),
        sa.Column("dataset_id", sa.Uuid, sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("inserted_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("external_id", "dataset_id", name="record_external_id_dataset_id_uq"),
    )


def downgrade() -> None:
    op.drop_table("records")
