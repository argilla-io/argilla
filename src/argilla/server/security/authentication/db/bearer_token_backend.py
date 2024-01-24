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
