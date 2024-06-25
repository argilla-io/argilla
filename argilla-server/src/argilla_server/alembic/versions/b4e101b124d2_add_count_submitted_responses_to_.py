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

"""add count_submitted_responses to records table

Revision ID: b4e101b124d2
Revises: 45a12f74448b
Create Date: 2024-06-24 17:07:18.614728

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b4e101b124d2"
down_revision = "45a12f74448b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("records", sa.Column("count_submitted_responses", sa.Integer(), server_default="0", nullable=False))
    op.execute("""
        UPDATE records
        SET count_submitted_responses = (
            SELECT COUNT(*)
            FROM responses
            WHERE responses.record_id = records.id AND responses.status = 'submitted'
        )
    """)


def downgrade() -> None:
    op.drop_column("records", "count_submitted_responses")
