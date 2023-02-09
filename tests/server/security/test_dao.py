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
from argilla.server.security.auth_provider.local.users.service import create_users_dao

usersDAO = create_users_dao()


# Test for function get_user class UserInDB
def test_get_user():
    user = usersDAO.get_user(user_name="argilla")
    assert user.username == "argilla"


# Test for function get_user_by_api_key class UserInDB
@pytest.mark.asyncio
async def test_get_user_by_api_key():
    user = await usersDAO.get_user_by_api_key(api_key=DEFAULT_API_KEY)
    assert user.username == "argilla"
