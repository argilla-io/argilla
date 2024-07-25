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

from pytest_mock import MockerFixture

from argilla_server.enums import UserRole
from argilla_server.integrations.huggingface.spaces import HuggingfaceSettings
from argilla_server.security.authentication.oauth2.providers import HuggingfaceClientProvider
from argilla_server.security.authentication.oauth2.providers import _huggingface


class TestHuggingfaceOauthProvider:
    def test_parse_role_from_userinfo_for_space_author(self, mocker: "MockerFixture"):
        mocker.patch.object(_huggingface, "HUGGINGFACE_SETTINGS", HuggingfaceSettings(space_author_name="author"))

        userinfo = {"preferred_username": "author"}
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.owner

    def test_parse_role_without_spaces_info(self, mocker: "MockerFixture"):
        mocker.patch.object(_huggingface, "HUGGINGFACE_SETTINGS", HuggingfaceSettings(space_author_name=None))

        userinfo = {"preferred_username": "author"}
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.annotator

    def test_parse_role_with_different_author_name(self, mocker: "MockerFixture"):
        mocker.patch.object(_huggingface, "HUGGINGFACE_SETTINGS", HuggingfaceSettings(space_author_name="other"))

        userinfo = {"preferred_username": "author"}
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.annotator

    def test_parse_role_with_missing_username(self):
        userinfo = {}
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.annotator

    def test_parse_role_with_admin_role_in_org(self, mocker: "MockerFixture"):
        mocker.patch.object(_huggingface, "HUGGINGFACE_SETTINGS", HuggingfaceSettings(space_author_name="org"))

        userinfo = {
            "preferred_username": "author",
            "orgs": [{"preferred_username": "org", "roleInOrg": "admin"}],
        }
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.owner

    def test_parse_role_with_non_admin_role_in_org(self, mocker: "MockerFixture"):
        mocker.patch.object(_huggingface, "HUGGINGFACE_SETTINGS", HuggingfaceSettings(space_author_name="org"))

        userinfo = {
            "preferred_username": "author",
            "orgs": [{"preferred_username": "org", "roleInOrg": "contributor"}],
        }
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.annotator

    def test_parse_role_for_other_org_author(self, mocker: "MockerFixture"):
        mocker.patch.object(_huggingface, "HUGGINGFACE_SETTINGS", HuggingfaceSettings(space_author_name="other_org"))

        userinfo = {
            "preferred_username": "author",
            "orgs": [{"preferred_username": "org", "roleInOrg": "contributor"}],
        }
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.annotator

    def test_parse_role_with_missing_org_role_info(self, mocker: "MockerFixture"):
        mocker.patch.object(_huggingface, "HUGGINGFACE_SETTINGS", HuggingfaceSettings(space_author_name="org"))

        userinfo = {
            "preferred_username": "author",
            "orgs": [{"preferred_username": "org"}],
        }
        role = HuggingfaceClientProvider.parse_role_from_userinfo(userinfo)
        assert role == UserRole.annotator
