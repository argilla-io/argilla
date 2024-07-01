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

"""add metadata column to records table

Revision ID: 3ff6484f8b37
Revises: ae5522b4c674
Create Date: 2023-06-14 13:02:41.735153

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3ff6484f8b37"
down_revision = "ae5522b4c674"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("records", sa.Column("metadata", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("records", "metadata")
