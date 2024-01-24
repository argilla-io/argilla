from typing import Dict, Optional, Tuple

from fastapi import Request
from fastapi.security import HTTPBearer
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser

from argilla.server.security.authentication.jwt import JWT
from argilla.server.security.authentication.oauth2.client_provider import OAuth2ClientProvider
from argilla.server.security.authentication.user import User


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
        user = User(token_data)

        provider = self.providers.get(user.get("provider"))
        claims = provider.claims if provider else {}

        return AuthCredentials(user.pop("scope", [])), user.use_claims(claims)
