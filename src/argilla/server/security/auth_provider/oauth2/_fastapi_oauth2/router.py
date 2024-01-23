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

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.enums import UserRole
from argilla.server.security.auth_provider.oauth2._fastapi_oauth2.middleware import Auth, User
from argilla.server.security.model import UserCreate

router = APIRouter(prefix="/oauth2")


@router.get("/{provider}/authorize")
def authorize(request: Request, provider: str):
    if request.auth.ssr:
        return request.auth.clients[provider].authorization_redirect(request)
    return dict(url=request.auth.clients[provider].authorization_url(request))


@router.get("/{provider}/token")
async def token(request: Request, provider: str):
    if request.auth.ssr:
        return await request.auth.clients[provider].token_redirect(request)
    return await request.auth.clients[provider].token_data(request)


@router.get("/{provider}/access-token")
async def token(request: Request, provider: str, db: AsyncSession = Depends(get_async_db)) -> dict:
    current_user = User(await request.auth.clients[provider].token_data(request))

    claims = Auth.clients[provider].claims
    current_user.use_claims(claims)
    username = current_user.username

    user = await accounts.get_user_by_username(db, username)
    if not user:
        user_create = UserCreate(
            first_name=current_user.name,
            username=username,
            role=UserRole.annotator,
            password="12345678",
        )
        await accounts.create_user(db, user_create)

    return {"access_token": request.auth.jwt_create(current_user)}


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(request.base_url)
    response.delete_cookie("Authorization")
    return response
