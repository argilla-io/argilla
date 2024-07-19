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

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server import telemetry
from argilla_server.api.schemas.v1.oauth2 import Provider, Providers, Token
from argilla_server.contexts import accounts
from argilla_server.database import get_async_db
from argilla_server.errors.future import AuthenticationError
from argilla_server.security.authentication.jwt import JWT
from argilla_server.security.authentication.oauth2 import OAuth2ClientProvider
from argilla_server.security.authentication.userinfo import UserInfo
from argilla_server.security.settings import settings

router = APIRouter(prefix="/oauth2", tags=["Authentication"])


def check_oauth_enabled_or_raise() -> None:
    if not settings.oauth.enabled:
        raise HTTPException(status_code=404, detail="OAuth2 is not enabled")


def _get_provider_by_name_or_raise(provider_name: str) -> OAuth2ClientProvider:
    if provider_name not in settings.oauth.providers:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")
    return settings.oauth.providers[provider_name]


@router.get("/providers", response_model=Providers)
def list_providers(_request: Request) -> Providers:
    if not settings.oauth.enabled:
        return Providers(items=[])

    return Providers(items=[Provider(name=provider_name) for provider_name in settings.oauth.providers])


@router.get("/providers/{provider}/authentication")
def get_authentication(
    request: Request,
    provider: str,
    _oauth_enabled: None = Depends(check_oauth_enabled_or_raise),
) -> RedirectResponse:
    provider = _get_provider_by_name_or_raise(provider)
    return provider.authorization_redirect(request)


@router.get("/providers/{provider}/access-token", response_model=Token)
async def get_access_token(
    request: Request,
    provider: str,
    db: AsyncSession = Depends(get_async_db),
    _oauth_enabled: None = Depends(check_oauth_enabled_or_raise),
) -> Token:
    try:
        provider = _get_provider_by_name_or_raise(provider)
        user_info = UserInfo(await provider.get_user_data(request))

        user_info.use_claims(provider.claims)
        username = user_info.username

        user = await accounts.get_user_by_username(db, username)
        if user and user.role != user_info.role:
            raise AuthenticationError("Could not authenticate user")
        elif user is None:
            user = await accounts.create_user_with_random_password(
                db,
                username=username,
                first_name=user_info.name,
                role=user_info.role,
                workspaces=[workspace.name for workspace in settings.oauth.allowed_workspaces],
            )
            telemetry.track_user_created(user, is_oauth=True)

        return Token(access_token=JWT.create(user_info))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # TODO: Create exception handler for AuthenticationError
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
