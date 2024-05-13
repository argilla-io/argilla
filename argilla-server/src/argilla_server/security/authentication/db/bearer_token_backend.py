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
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser

from argilla_server.contexts import accounts
from argilla_server.security.authentication.jwt import JWT
from argilla_server.security.authentication.userinfo import UserInfo


class BearerTokenAuthenticationBackend(AuthenticationBackend):
    """Authenticate the user using the username and password Bearer header"""

    scheme = HTTPBearer(auto_error=False)

    async def authenticate(self, request: Request) -> typing.Optional[typing.Tuple[AuthCredentials, BaseUser]]:
        """Authenticate the user using the username and password Bearer header"""
        credentials = await self.scheme(request)
        if not credentials:
            return None

        token = credentials.credentials
        username = JWT.decode(token).get("username")

        db = request.state.db
        user = await accounts.get_user_by_username(db, username)
        if not user:
            return None

        return AuthCredentials(), UserInfo(
            username=user.username, name=user.first_name, role=user.role, identity=str(user.id)
        )
