#  coding=utf-8
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

from fastapi import Depends
from fastapi.security import APIKeyHeader, SecurityScopes

from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import User

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


class AuthProvider:
    """Base class for auth provider"""

    async def get_user(
        self,
        security_scopes: SecurityScopes,
        api_key: Optional[str] = Depends(api_key_header),
        **kwargs,
    ) -> User:
        raise NotImplementedError()
