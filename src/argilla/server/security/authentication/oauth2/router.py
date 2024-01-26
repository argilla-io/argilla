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
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.pydantic_v1 import BaseModel
from argilla.server.security.authentication.jwt import JWT
from argilla.server.security.authentication.user import User
from argilla.server.security.model import Token
from argilla.server.security.settings import settings

router = APIRouter(prefix="/oauth2/providers")


class Provider(BaseModel):
    name: str


class Providers(BaseModel):
    items: List[Provider]


@router.get("")
def list_providers(_: Request) -> Providers:
    items = []

    if settings.oauth2.enabled:
        items = [Provider(name=provider_name) for provider_name in settings.oauth2.providers]

    return Providers(items=items)


if settings.oauth2.enabled:

    @router.get("/{provider}/authentication")
    def authorize(request: Request, provider: str):
        return settings.oauth2.providers[provider].authorization_redirect(request)

    @router.get("/{provider}/access-token")
    async def get_access_token(request: Request, provider: str, db: AsyncSession = Depends(get_async_db)) -> Token:
        current_user = User(await settings.oauth2.providers[provider].token_data(request))

        claims = settings.oauth2.providers[provider].claims
        current_user.use_claims(claims)
        username = current_user.username

        user = await accounts.get_user_by_username(db, username)
        if not user:
            await accounts.create_oauth2_user(
                db,
                username=username,
                name=current_user.name,
                workspaces=[workspace.name for workspace in settings.oauth2.allowed_workspaces],
            )

        return Token(access_token=JWT.create(current_user))
