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

from typing import Optional

from fastapi import Depends, FastAPI
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

import argilla.server.schemas.v0.users
from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.errors import UnauthorizedError
from argilla.server.security.authentication import db
from argilla.server.security.authentication.db import APIKeyAuthenticationBackend, BearerTokenAuthenticationBackend


class AuthenticationProvider:
    backends = [APIKeyAuthenticationBackend(), BearerTokenAuthenticationBackend()]

    @classmethod
    def new_instance(cls):
        return AuthenticationProvider()

    def configure_app(self, app: FastAPI) -> None:
        app.include_router(db.router, prefix="/api/security", tags=["security"])

    async def get_current_user(
        self,
        _: SecurityScopes,
        request: Request,
        db: AsyncSession = Depends(get_async_db),
        _api_key: Optional[str] = Depends(APIKeyAuthenticationBackend.scheme),
        _bearer: Optional[str] = Depends(BearerTokenAuthenticationBackend.scheme),
    ) -> argilla.server.schemas.v0.users.User:
        # This db will be used by the backends. Ideally this should be done as a global dependency
        # but is not working as expected. Sometimes the db is not available in the request state at the
        # middlewares level.
        request.state.db = db

        userinfo = None
        for backend in self.backends:
            if results := await backend.authenticate(request):
                _, userinfo = results
                break

        if not userinfo:
            raise UnauthorizedError()

        user = await accounts.get_user_by_username(db, userinfo.username)
        if not user:
            raise UnauthorizedError()

        return user
