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

from typing import Any, Optional

from starlette.authentication import BaseUser

from argilla_server.enums import UserRole
from argilla_server.security.authentication.claims import Claims

_DEFAULT_USER_ROLE = UserRole.annotator


class UserInfo(BaseUser, dict):
    """User info from a provider."""

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def username(self) -> str:
        return self["username"]

    @property
    def first_name(self) -> str:
        return self.get("first_name") or self.username

    @property
    def role(self) -> UserRole:
        role = self.get("role") or _DEFAULT_USER_ROLE
        return UserRole(role)

    def use_claims(self, claims: Optional[Claims]) -> "UserInfo":
        claims = claims or {}

        for attr, item in claims.items():
            self[attr] = self.__getprop__(item)

        return self

    def __getprop__(self, item, default="") -> Any:
        if callable(item):
            return item(self)
        return self.get(item, default)

    __getattr__ = __getprop__
