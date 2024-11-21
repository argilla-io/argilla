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

"""add datasets_users table

Revision ID: 580a6553186f
Revises: 6ed1b8bf8e08
Create Date: 2024-11-20 12:15:24.631417

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "580a6553186f"
down_revision = "6ed1b8bf8e08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "datasets_users",
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("inserted_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dataset_id", "user_id"),
    )
    op.create_index(op.f("ix_datasets_users_dataset_id"), "datasets_users", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_datasets_users_user_id"), "datasets_users", ["user_id"], unique=False)

    bind = op.get_bind()

    statement = """
        INSERT INTO datasets_users (dataset_id, user_id, inserted_at, updated_at)
        SELECT dataset_id, user_id, {now_func}, {now_func} FROM (
            SELECT DISTINCT records.dataset_id AS dataset_id, responses.user_id as user_id
            FROM responses
            JOIN records ON records.id = responses.record_id
        ) AS subquery
    """

    if bind.dialect.name == "postgresql":
        op.execute(statement.format(now_func="NOW()"))
    elif bind.dialect.name == "sqlite":
        op.execute(statement.format(now_func="datetime('now')"))
    else:
        raise Exception("Unsupported database dialect")


def downgrade() -> None:
    op.drop_index(op.f("ix_datasets_users_user_id"), table_name="datasets_users")
    op.drop_index(op.f("ix_datasets_users_dataset_id"), table_name="datasets_users")
    op.drop_table("datasets_users")
