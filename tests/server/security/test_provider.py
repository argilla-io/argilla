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

import pytest
from argilla._constants import DEFAULT_API_KEY
from argilla.server.security.auth_provider.local.provider import (
    create_local_auth_provider,
)
from fastapi.security import SecurityScopes

localAuth = create_local_auth_provider()
security_Scopes = SecurityScopes


# Tests for function get_user via token and api key
@pytest.mark.asyncio
async def test_get_user_via_token():
    access_token = localAuth._create_access_token(username="argilla")
    user = await localAuth.get_user(security_scopes=security_Scopes, token=access_token)
    assert user.username == "argilla"


@pytest.mark.asyncio
async def test_get_user_via_api_key():
    user = await localAuth.get_user(security_scopes=security_Scopes, api_key=DEFAULT_API_KEY)
    assert user.username == "argilla"


# Test for function find user by api key token
@pytest.mark.asyncio
async def test_get_user_by_api_key():
    user = await localAuth._find_user_by_api_key(api_key=DEFAULT_API_KEY)
    assert user.username == "argilla"


# Test for function fetch token
def test_fetch_token_user():
    access_token = localAuth._create_access_token(username="argilla")
    user = localAuth.fetch_token_user(token=access_token)
    assert user.username == "argilla"
