# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from uuid import UUID

from argilla.users._resource import User

__all__ = ["User", "DELETED_USER", "is_deleted_user_id"]

# This is the user id for the deleted user. Used when records contains responses from a user that has been deleted.
DELETED_USER = User(id=UUID("00000000-0000-0000-0000-000000000000"), username="deleted")


def is_deleted_user_id(user_id: UUID) -> bool:
    """Check if a specific user id is the delete user id

    Returns:
        True: If the provided user id is the DELETE_USER.id. False, otherwise
    """
    return DELETED_USER.id == user_id
