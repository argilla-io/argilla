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

from argilla_server.security.authentication.oauth2._backends import KeycloakOpenId, Strategy


class TestKeyCloackOpenIdBackend:
    def test_get_user_details_with_argilla_role(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"roles": ["role1", "role2", "argilla_role:annotator"]},
            }
        )

        assert user_details["role"] == "annotator"

    def test_get_user_details_with_wrong_argilla_role_definition(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"roles": ["role1", "role2", "argilla_role=annotator"]},
            }
        )

        assert "role" not in user_details

    def test_get_user_details_without_argilla_role(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"roles": ["role1", "role2"]},
            }
        )

        assert "role" not in user_details

    def test_get_user_details_with_argilla_workspaces(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"roles": ["role1", "role2", "argilla_workspace:ws1"]},
            }
        )

        assert user_details["available_workspaces"] == ["ws1"]

    def test_get_user_details_with_wrong_argilla_workspace_definition(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"roles": ["role1", "role2", "argilla_workspace=ws1"]},
            }
        )

        assert "available_workspaces" not in user_details

    def test_get_user_details_with_multiple_argilla_workspaces(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"roles": ["role1", "role2", "argilla_workspace:ws1", "argilla_workspace:ws2"]},
            }
        )

        assert user_details["available_workspaces"] == ["ws1", "ws2"]

    def test_get_user_details_with_missing_argilla_workspaces(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"roles": ["role1", "role2"]},
            }
        )

        assert "available_workspaces" not in user_details

    def test_get_user_details_with_missing_roles_key(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details(
            {
                "realm_access": {"other": "stuff"},
            }
        )

        assert "role" not in user_details
        assert "available_workspaces" not in user_details

    def test_get_user_details_with_missing_realm_access_key(self):
        backend = KeycloakOpenId(strategy=Strategy())

        user_details = backend.get_user_details({"other": "stuff"})

        assert "role" not in user_details
        assert "available_workspaces" not in user_details
