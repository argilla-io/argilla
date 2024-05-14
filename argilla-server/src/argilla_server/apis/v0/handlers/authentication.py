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
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts import accounts
from argilla_server.database import get_async_db
from argilla_server.errors import UnauthorizedError
from argilla_server.schemas.v0.authentication import Token, UserPasswordRequestForm
from argilla_server.security.authentication.jwt import JWT
from argilla_server.security.authentication.userinfo import UserInfo

router = APIRouter(tags=["Authentication"])


@router.post("/security/token", response_model=Token)
async def create_access_token(
    db: AsyncSession = Depends(get_async_db), form: UserPasswordRequestForm = Depends()
) -> Token:
    user = await accounts.authenticate_user(db, form.username, form.password)
    if not user:
        raise UnauthorizedError()

    token = JWT.create(UserInfo(username=user.username, name=user.first_name, role=user.role, identity=str(user.id)))

    return Token(access_token=token)
