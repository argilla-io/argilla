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

"""fix suggestions type enum values

Revision ID: 1e629a913727
Revises: 3fc3c0839959
Create Date: 2023-07-24 12:47:11.715011

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "1e629a913727"
down_revision = "3fc3c0839959"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE suggestion_type_enum ADD VALUE IF NOT EXISTS 'model';")
        op.execute("ALTER TYPE suggestion_type_enum ADD VALUE IF NOT EXISTS 'human';")


def downgrade() -> None:
    pass
