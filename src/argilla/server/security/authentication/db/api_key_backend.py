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

from typing import Optional, Tuple

from fastapi import Request
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser

from argilla.server.constants import API_KEY_HEADER_NAME
from argilla.server.contexts import accounts
from argilla.server.security.authentication.user import User


class APIKeyAuthenticationBackend(AuthenticationBackend):
    scheme = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        """Authenticate the user using the API Key header"""
        api_key: str = await self.scheme(request)

        if not api_key:
            return None

        db = self.db
        user = await accounts.get_user_by_api_key(db, api_key=api_key)

        if not user:
            return None

        #  TODO: Create a ArgillaUser with more user info
        return AuthCredentials(["authenticated"]), User(username=user.username)
