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
import os

import pytest
from pytest_mock import MockerFixture

from argilla_server.enums import UserRole
from argilla_server.security.authentication import UserInfo


class TestUserInfo:
    def test_get_user_name_without_claims(self):
        userinfo = UserInfo()
        with pytest.raises(KeyError):
            userinfo.username  # noqa

    def test_get_userinfo_first_name(self):
        userinfo = UserInfo({"username": "user", "first_name": "User"})
        assert userinfo.first_name == "User"

    def test_get_default_userinfo_first_name(self):
        userinfo = UserInfo({"username": "user"})
        assert userinfo.first_name == "user"

    def test_get_default_userinfo_role(self):
        userinfo = UserInfo({"username": "user"})
        assert userinfo.role == UserRole.annotator

    def test_get_userinfo_role(self):
        userinfo = UserInfo({"username": "user", "role": "owner"})
        assert userinfo.role == UserRole.owner

    def test_get_userinfo_role_with_username_env(self, mocker: MockerFixture):
        mocker.patch.dict(os.environ, {"USERNAME": "user"})

        userinfo = UserInfo({"username": "user"})
        assert userinfo.role == UserRole.owner
