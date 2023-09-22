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
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.errors import UnauthorizedError
from argilla.server.schemas.v0.security import Token
from argilla.server.security.auth_provider import LocalAuthProvider, create_local_auth_provider
from argilla.server.security.auth_provider.local.provider import SECURITY_TOKEN_PATH

router = APIRouter(tags=["security"])


@router.post(SECURITY_TOKEN_PATH, response_model=Token, operation_id="login_for_access_token")
async def login_for_access_token(
    db: AsyncSession = Depends(get_async_db),
    auth_provider: LocalAuthProvider = Depends(create_local_auth_provider),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = await accounts.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise UnauthorizedError()

    access_token = auth_provider.create_access_token(user.username)
    return Token(access_token=access_token)
