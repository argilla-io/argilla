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

from typing import Dict, Optional, Tuple

from fastapi import Request
from fastapi.security import HTTPBearer
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser

from argilla_server.security.authentication.jwt import JWT
from argilla_server.security.authentication.oauth2.providers import OAuth2ClientProvider
from argilla_server.security.authentication.userinfo import UserInfo


class OAuth2AuthenticationBackend(AuthenticationBackend):
    """Authentication backend for AuthenticationMiddleware."""

    scheme = HTTPBearer(auto_error=False)

    def __init__(self, providers: Dict[str, OAuth2ClientProvider]) -> None:
        self.providers = providers

    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        credentials = await self.scheme(request)
        if credentials is None:
            return None

        token_data = JWT.decode(credentials.credentials)
        user = UserInfo(token_data)

        provider = self.providers.get(user.get("provider"))
        claims = provider.claims if provider else {}

        return AuthCredentials(user.pop("scope", [])), user.use_claims(claims)
