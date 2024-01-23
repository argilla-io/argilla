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

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette.requests import Request

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
async def token(request: Request, provider: str) -> dict:
    access_token = await request.auth.clients[provider].fetch_access_token(request)
    return {"access_token": access_token}


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(request.base_url)
    response.delete_cookie("Authorization")
    return response
