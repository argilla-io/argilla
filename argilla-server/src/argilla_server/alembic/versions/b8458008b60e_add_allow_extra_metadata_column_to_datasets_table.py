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

"""add allow_extra_metadata column to datasets table

Revision ID: b8458008b60e
Revises: 7cbcccf8b57a
Create Date: 2023-09-29 13:51:44.525944

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b8458008b60e"
down_revision = "7cbcccf8b57a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "datasets", sa.Column("allow_extra_metadata", sa.Boolean(), server_default=sa.text("true"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("datasets", "allow_extra_metadata")
