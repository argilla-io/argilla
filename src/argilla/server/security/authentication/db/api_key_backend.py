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
