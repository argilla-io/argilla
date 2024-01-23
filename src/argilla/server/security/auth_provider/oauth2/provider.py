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

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.security import SecurityScopes
from social_core.backends.open_id_connect import OpenIdConnectAuth
from sqlalchemy.ext.asyncio import AsyncSession

from argilla.server import models
from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.errors import UnauthorizedError
from argilla.server.security.auth_provider.base import AuthProvider, api_key_header
from ._fastapi_oauth2.claims import Claims
from ._fastapi_oauth2.client import OAuth2Client
from ._fastapi_oauth2.config import OAuth2Config
from ._fastapi_oauth2.middleware import Auth, OAuth2Middleware, User
from ._fastapi_oauth2.router import router as oauth2_router
from ._fastapi_oauth2.security import OAuth2
from .. import settings

from .. import settings
from ._fastapi_oauth2.claims import Claims
from ._fastapi_oauth2.client import OAuth2Client
from ._fastapi_oauth2.config import OAuth2Config
from ._fastapi_oauth2.middleware import Auth, OAuth2Middleware, User
from ._fastapi_oauth2.router import router as oauth2_router
from ._fastapi_oauth2.security import OAuth2


class HuggingfaceOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "huggingface"

    OIDC_ENDPOINT = "https://huggingface.co"
    AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
    ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

    def oidc_endpoint(self) -> str:
        return self.OIDC_ENDPOINT


class OAuth2Provider(AuthProvider):
    oauth2 = OAuth2(auto_error=False)

    def __init__(self, config: OAuth2Config):
        self.config = config

    @classmethod
    def new_instance(cls):
        oauth2_config = OAuth2Config(
            allow_http=settings.insecure_mode,
            jwt_secret=settings.secret_key,
            jwt_expires=settings.token_expire_time,
            jwt_algorithm=settings.algorithm,
            clients=[
                OAuth2Client(
                    backend=HuggingfaceOpenId,
                    client_id=os.getenv("OAUTH2_HF_CLIENT_ID"),
                    client_secret=os.getenv("OAUTH2_HF_CLIENT_SECRET"),
                    scope=os.getenv("OAUTH2_HF_SCOPE").split(",")
                    if os.getenv("OAUTH2_HF_SCOPE")
                    else HuggingfaceOpenId.DEFAULT_SCOPE,
                    redirect_uri=os.getenv("OAUTH2_HF_REDIRECT_URI"),
                    claims=Claims(
                        username="preferred_username",
                        first_name="name",
                    ),
                ),
            ],
        )
        load_dotenv()

        return cls(oauth2_config)

    def configure_app(self, app: FastAPI):
        @oauth2_router.get("/providers")
        def providers(request: Request) -> dict:
            auth: Auth = request.auth
            return {"items": [{"name": name} for name in auth.clients.keys()]}

        @oauth2_router.get("/me")
        def me(request: Request) -> dict:
            return request.user

        app.include_router(oauth2_router, tags=["security"])
        app.add_middleware(OAuth2Middleware, config=self.config)

    def callback(self, _: Auth, user: User):
        print("HERE IN CALLBACK", user)

    async def get_current_user(
        self,
        security_scopes: SecurityScopes,
        request: Request,
        db: AsyncSession = Depends(get_async_db),
        api_key: Optional[str] = Depends(api_key_header),
        _: str = Depends(oauth2),
    ) -> models.User:
        if api_key:
            user = await accounts.get_user_by_api_key(db, api_key)
        else:
            print("GET CURRENT USER", request.user.username)
            user = await accounts.get_user_by_username(db, request.user.username)

        if not user:
            raise UnauthorizedError()

        return user
