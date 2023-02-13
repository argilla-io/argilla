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

"""create organizations table

Revision ID: b39023f927f6
Revises: 74694870197c
Create Date: 2023-02-13 17:54:20.695113

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b39023f927f6"
down_revision = "74694870197c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("organizations")
