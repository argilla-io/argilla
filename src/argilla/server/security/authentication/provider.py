from typing import Optional

from fastapi import APIRouter, Depends, FastAPI
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request

import argilla.server.schemas.v0.users
from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.errors import UnauthorizedError
from argilla.server.security.authentication.db import APIKeyAuthenticationBackend, BearerTokenAuthenticationBackend
from argilla.server.security.authentication.oauth2 import OAuth2AuthenticationBackend
from . import db, oauth2
from ..settings import settings


class AuthenticationProvider:
    @classmethod
    def new_instance(cls):
        return AuthenticationProvider()

    def configure_app(self, app: FastAPI) -> None:
        router = APIRouter(prefix="/api/security", tags=["security"])
        router.include_router(router=db.router)
        router.include_router(router=oauth2.router)

        if settings.oauth2.enabled:
            app.add_middleware(
                AuthenticationMiddleware, backend=OAuth2AuthenticationBackend(providers=settings.oauth2.providers)
            )

        app.include_router(router)

    async def get_current_user(
        self,
        security_scopes: SecurityScopes,
        request: Request,
        db: AsyncSession = Depends(get_async_db),
        _api_key: Optional[str] = Depends(APIKeyAuthenticationBackend.scheme),
        _bearer: Optional[str] = Depends(BearerTokenAuthenticationBackend.scheme),
    ) -> argilla.server.schemas.v0.users.User:
        if results := await APIKeyAuthenticationBackend(db).authenticate(request):
            _, request_user = results
        elif results := await BearerTokenAuthenticationBackend(db=db).authenticate(request):
            _, request_user = results
        else:
            raise UnauthorizedError()

        user = await accounts.get_user_by_username(db, request_user.username)
        if not user:
            raise UnauthorizedError()

        return user
