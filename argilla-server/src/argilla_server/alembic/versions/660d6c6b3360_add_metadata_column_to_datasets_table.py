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

"""add metadata column to datasets table

Revision ID: 660d6c6b3360
Revises: 237f7c674d74
Create Date: 2024-10-04 16:47:21.611404

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "660d6c6b3360"
down_revision = "237f7c674d74"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("datasets", sa.Column("metadata", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("datasets", "metadata")
