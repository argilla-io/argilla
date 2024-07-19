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

"""add status column to records table

Revision ID: 237f7c674d74
Revises: 45a12f74448b
Create Date: 2024-06-18 17:59:36.992165

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "237f7c674d74"
down_revision = "45a12f74448b"
branch_labels = None
depends_on = None


record_status_enum = sa.Enum("pending", "completed", name="record_status_enum")


def upgrade() -> None:
    record_status_enum.create(op.get_bind())

    op.add_column("records", sa.Column("status", record_status_enum, server_default="pending", nullable=False))
    op.create_index(op.f("ix_records_status"), "records", ["status"], unique=False)

    # NOTE: Updating existent records to have "completed" status when they have
    # at least one response with "submitted" status.
    op.execute("""
        UPDATE records
        SET status = 'completed'
        WHERE id IN (
            SELECT DISTINCT record_id
            FROM responses
            WHERE status = 'submitted'
        );
    """)


def downgrade() -> None:
    op.drop_index(op.f("ix_records_status"), table_name="records")
    op.drop_column("records", "status")

    record_status_enum.drop(op.get_bind())
