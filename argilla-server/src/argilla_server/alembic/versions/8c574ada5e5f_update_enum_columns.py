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

"""update_enum_columns

Revision ID: 8c574ada5e5f
Revises: 3ff6484f8b37
Create Date: 2023-06-23 15:55:19.928164

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8c574ada5e5f"
down_revision = "3ff6484f8b37"
branch_labels = None
depends_on = None

# Aligned with the values of `ResponseStatus` in `src/argilla/server/models/dataset.py`
response_status_enum = sa.Enum("draft", "submitted", "discarded", name="response_status_enum")

# Aligned with the values of `DatasetStatus` in `src/argilla/server/models/dataset.py`
dataset_status_enum = sa.Enum("draft", "ready", name="dataset_status_enum")

# Aligned with the values of `UserRole` in `src/argilla/server/models/dataset.py`
user_role_enum = sa.Enum("owner", "admin", "annotator", name="user_role_enum")


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        response_status_enum.create(bind)
        op.execute(
            "ALTER TABLE responses ALTER COLUMN status TYPE response_status_enum USING status::response_status_enum"
        )

        dataset_status_enum.create(bind)
        op.execute(
            "ALTER TABLE datasets ALTER COLUMN status TYPE dataset_status_enum USING status::dataset_status_enum"
        )

        user_role_enum.create(bind)
        op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role_enum USING role::user_role_enum")


def downgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column("role", existing_type=user_role_enum, type_=sa.String(), nullable=False)
        user_role_enum.drop(bind)

        with op.batch_alter_table("datasets") as batch_op:
            batch_op.alter_column("status", existing_type=dataset_status_enum, type_=sa.String(), nullable=False)
        dataset_status_enum.drop(bind)

        with op.batch_alter_table("responses") as batch_op:
            batch_op.alter_column("status", existing_type=response_status_enum, type_=sa.String(), nullable=False)
        response_status_enum.drop(bind)
