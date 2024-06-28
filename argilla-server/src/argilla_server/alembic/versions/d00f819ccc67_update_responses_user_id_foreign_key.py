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

"""update responses user_id foreign key

Revision ID: d00f819ccc67
Revises: ca7293c38970
Create Date: 2024-06-27 18:04:46.080762

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d00f819ccc67"
down_revision = "ca7293c38970"
branch_labels = None
depends_on = None


CONSTRAINT_NAME = "responses_user_id_fkey"
NAMING_CONVENTION = {"fk": "%(table_name)s_%(column_0_name)s_fkey"}


def upgrade() -> None:
    op.execute("DELETE FROM responses WHERE user_id IS NULL")

    with op.batch_alter_table("responses", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Uuid(), nullable=False)
        batch_op.drop_constraint(CONSTRAINT_NAME, type_="foreignkey")
        batch_op.create_foreign_key(CONSTRAINT_NAME, "users", ["user_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    with op.batch_alter_table("responses", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Uuid(), nullable=True)
        batch_op.drop_constraint(CONSTRAINT_NAME, type_="foreignkey")
        batch_op.create_foreign_key(CONSTRAINT_NAME, "users", ["user_id"], ["id"], ondelete="SET NULL")
