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

from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.errors.future import NotUniqueError, UnprocessableEntityError
from argilla_server.models import User


class UserCreateValidator:
    @classmethod
    async def validate(cls, db: AsyncSession, user: User) -> None:
        await cls._validate_username(db, user)

    @classmethod
    async def _validate_username(cls, db, user: User):
        await cls._validate_username_length(user)
        await cls._validate_unique_username(db, user)

    @classmethod
    async def _validate_unique_username(cls, db, user):
        from argilla_server.contexts import accounts

        if await accounts.get_user_by_username(db, user.username) is not None:
            raise NotUniqueError(f"User username `{user.username}` is not unique")

    @classmethod
    async def _validate_username_length(cls, user: User):
        if len(user.username) < 1:
            raise UnprocessableEntityError("Username must be at least 1 characters long")
