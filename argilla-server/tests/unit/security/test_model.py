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

from argilla_server.api.schemas.v1.users import User, UserCreate
from tests.factories import UserFactory


@pytest.mark.parametrize(
    "username",
    [
        "user-name",
        "user_name",
        "user123",
        "user-123",
        "user_123",
        "UserName",
        "userName",
        "User_name",
        "valid_user_name",
        "user-123_abc",
        "user_123-abc",
        "0033_user",
        "12-user",
    ],
)
def test_user_create(username: str):
    assert UserCreate(first_name="first-name", username=username, password="12345678")


@pytest.mark.asyncio
async def test_user_first_name():
    user = await UserFactory.create(first_name="first-name", workspaces=[])

    assert User.model_validate(user).first_name == "first-name"


@pytest.mark.asyncio
async def test_user_last_name():
    user = await UserFactory.create(last_name="last-name", workspaces=[])

    assert User.model_validate(user).last_name == "last-name"
