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

from argilla.server.errors import ForbiddenOperationError
from argilla.server.security.model import User


def validate_is_super_user(user: User, message: str = None):
    """Common validation to ensure the current user is a admin/superuser"""
    if not user.is_superuser():
        raise ForbiddenOperationError(message or "Only admin users can apply this change")
