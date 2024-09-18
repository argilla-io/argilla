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

"""add distribution column to datasets table

Revision ID: 45a12f74448b
Revises: d00f819ccc67
Create Date: 2024-06-13 11:23:43.395093

"""

import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "45a12f74448b"
down_revision = "d00f819ccc67"
branch_labels = None
depends_on = None

DISTRIBUTION_VALUE = json.dumps({"strategy": "overlap", "min_submitted": 1})


def upgrade() -> None:
    op.add_column("datasets", sa.Column("distribution", sa.JSON(), nullable=True))
    op.execute(f"UPDATE datasets SET distribution = '{DISTRIBUTION_VALUE}'")
    with op.batch_alter_table("datasets") as batch_op:
        batch_op.alter_column("distribution", nullable=False)


def downgrade() -> None:
    op.drop_column("datasets", "distribution")
