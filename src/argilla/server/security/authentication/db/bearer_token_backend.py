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

import typing

from fastapi import Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser

from argilla.server.contexts import accounts
from argilla.server.security.authentication.jwt import JWT
from argilla.server.security.authentication.user import User


class BearerTokenAuthenticationBackend(AuthenticationBackend):
    scheme = HTTPBearer(auto_error=False)

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, request: Request) -> typing.Optional[typing.Tuple[AuthCredentials, BaseUser]]:
        """Authenticate the user using the username and password Bearer header"""
        credentials = await self.scheme(request)
        if not credentials:
            return None

        token = credentials.credentials
        username = JWT.decode(token).get("username")

        db = self.db
        if not await accounts.get_user_by_username(db, username):
            return None

        return AuthCredentials(["authenticated"]), User(username=username)
