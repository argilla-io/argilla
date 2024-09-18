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

from datetime import datetime, timedelta

from jose import JWTError, jwt

from argilla_server.errors import UnauthorizedError
from argilla_server.security.authentication.userinfo import UserInfo
from argilla_server.security.settings import settings


class JWT:
    secret: str = settings.secret_key
    algorithm: str = settings.algorithm
    expires: int = settings.token_expiration

    @classmethod
    def encode(cls, data: dict) -> str:
        return jwt.encode(data, cls.secret, algorithm=cls.algorithm)

    @classmethod
    def decode(cls, token: str) -> dict:
        try:
            return jwt.decode(token, cls.secret, algorithms=[cls.algorithm])
        except JWTError:
            raise UnauthorizedError("Invalid token")

    @classmethod
    def create(cls, user: UserInfo) -> str:
        expire = datetime.utcnow() + timedelta(seconds=cls.expires)
        return cls.encode({**user, "exp": expire})
