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

"""create metadata_properties table

Revision ID: 7cbcccf8b57a
Revises: 1e629a913727
Create Date: 2023-09-22 11:40:07.700301

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7cbcccf8b57a"
down_revision = "1e629a913727"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metadata_properties",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("name", sa.String, nullable=False, index=True),
        sa.Column("title", sa.Text, nullable=False),
        # TODO: We should move type column to settings as an attribute (as we are already doing for Fields and Questions).
        sa.Column("type", sa.String, nullable=False),
        sa.Column("settings", sa.JSON, nullable=False),
        sa.Column("allowed_roles", sa.JSON, server_default="[]"),
        sa.Column("dataset_id", sa.Uuid, sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("inserted_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("name", "dataset_id", name="metadata_property_name_dataset_id_uq"),
    )


def downgrade() -> None:
    op.drop_table("metadata_properties")
