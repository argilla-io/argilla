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

from unittest import mock

import pytest
from httpcore import URL
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.enums import UserRole
from argilla_server.errors.future import AuthenticationError
from argilla_server.models import User
from argilla_server.security.authentication import JWT
from argilla_server.security.authentication.oauth2 import OAuth2Settings
from tests.factories import AdminFactory, AnnotatorFactory


@pytest.fixture
def disabled_oauth_settings() -> OAuth2Settings:
    return OAuth2Settings(enabled=False)


@pytest.fixture
def default_oauth_settings() -> OAuth2Settings:
    return OAuth2Settings.from_dict(
        {
            "enabled": True,
            "providers": [
                {
                    "name": "huggingface",
                    "client_id": "client_id",
                    "client_secret": "client_secret",
                }
            ],
        }
    )


@pytest.mark.asyncio
class TestOauth2:
    async def tests_list_providers_with_default_config(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.get("/api/v1/oauth2/providers", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {"items": []}

    async def test_list_providers_with_oauth_disabled(
        self, async_client: AsyncClient, owner_auth_header: dict, disabled_oauth_settings: OAuth2Settings
    ):
        with mock.patch(
            "argilla_server.security.settings.Settings.oauth", new_callable=lambda: disabled_oauth_settings
        ):
            response = await async_client.get("/api/v1/oauth2/providers", headers=owner_auth_header)
            assert response.status_code == 200
            assert response.json() == {"items": []}

    async def test_list_provider_with_oauth_disabled_from_settings(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        default_oauth_settings.enabled = False
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get("/api/v1/oauth2/providers", headers=owner_auth_header)
            assert response.status_code == 200
            assert response.json() == {"items": []}

    async def test_list_providers(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get("/api/v1/oauth2/providers", headers=owner_auth_header)
            assert response.status_code == 200
            assert response.json() == {"items": [{"name": "huggingface"}]}

    async def test_provider_huggingface_authentication(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get(
                "/api/v1/oauth2/providers/huggingface/authentication?extra=params", headers=owner_auth_header
            )
            assert response.status_code == 303

            redirect_url = URL(response.headers.get("location"))
            assert redirect_url.scheme == b"https"
            assert redirect_url.host == b"huggingface.co"
            assert b"/oauth/authorize?response_type=code&client_id=client_id" in redirect_url.target
            assert b"&extra=params" in redirect_url.target

    async def test_provider_authentication_with_oauth_disabled(
        self,
        async_client: AsyncClient,
        owner_auth_header: dict,
        disabled_oauth_settings: OAuth2Settings,
    ):
        with mock.patch(
            "argilla_server.security.settings.Settings.oauth", new_callable=lambda: disabled_oauth_settings
        ):
            response = await async_client.get(
                "/api/v1/oauth2/providers/huggingface/authentication", headers=owner_auth_header
            )
            assert response.status_code == 404

    async def test_provider_authentication_with_oauth_disabled_and_provider_defined(
        self,
        async_client: AsyncClient,
        owner_auth_header: dict,
        default_oauth_settings: OAuth2Settings,
    ):
        default_oauth_settings.enabled = False
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get(
                "/api/v1/oauth2/providers/huggingface/authentication", headers=owner_auth_header
            )
            assert response.status_code == 404

    async def test_provider_authentication_with_invalid_provider(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get(
                "/api/v1/oauth2/providers/invalid/authentication", headers=owner_auth_header
            )
            assert response.status_code == 404

    async def test_provider_huggingface_access_token(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        owner_auth_header: dict,
        default_oauth_settings: OAuth2Settings,
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            with mock.patch(
                "argilla_server.security.authentication.oauth2.providers.OAuth2ClientProvider._fetch_user_data",
                return_value={"preferred_username": "username", "name": "name"},
            ):
                response = await async_client.get(
                    "/api/v1/oauth2/providers/huggingface/access-token",
                    params={"code": "code", "state": "valid"},
                    headers=owner_auth_header,
                    cookies={"oauth2_state": "valid"},
                )

                assert response.status_code == 200

                json_response = response.json()
                assert JWT.decode(json_response["access_token"])["username"] == "username"
                assert json_response["token_type"] == "bearer"

                user = await db.scalar(select(User).filter_by(username="username"))
                assert user is not None
                assert user.role == UserRole.annotator

    async def test_provider_huggingface_access_token_with_missing_username(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        owner_auth_header: dict,
        default_oauth_settings: OAuth2Settings,
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            with mock.patch(
                "argilla_server.security.authentication.oauth2.providers.OAuth2ClientProvider._fetch_user_data",
                return_value={"name": "name"},
            ):
                response = await async_client.get(
                    "/api/v1/oauth2/providers/huggingface/access-token",
                    params={"code": "code", "state": "valid"},
                    headers=owner_auth_header,
                    cookies={"oauth2_state": "valid"},
                )

                assert response.status_code == 500

    async def test_provider_huggingface_access_token_with_missing_name(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        owner_auth_header: dict,
        default_oauth_settings: OAuth2Settings,
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            with mock.patch(
                "argilla_server.security.authentication.oauth2.providers.OAuth2ClientProvider._fetch_user_data",
                return_value={"preferred_username": "username"},
            ):
                response = await async_client.get(
                    "/api/v1/oauth2/providers/huggingface/access-token",
                    params={"code": "code", "state": "valid"},
                    headers=owner_auth_header,
                    cookies={"oauth2_state": "valid"},
                )

                assert response.status_code == 200

                json_response = response.json()
                assert JWT.decode(json_response["access_token"])["username"] == "username"
                assert json_response["token_type"] == "bearer"

                user = await db.scalar(select(User).filter_by(username="username"))
                assert user is not None
                assert user.role == UserRole.annotator
                assert user.first_name == "username"

    async def test_provider_access_token_with_oauth_disabled(
        self,
        async_client: AsyncClient,
        owner_auth_header: dict,
        disabled_oauth_settings: OAuth2Settings,
    ):
        with mock.patch(
            "argilla_server.security.settings.Settings.oauth", new_callable=lambda: disabled_oauth_settings
        ):
            response = await async_client.get(
                "/api/v1/oauth2/providers/huggingface/access-token", headers=owner_auth_header
            )
            assert response.status_code == 404

    async def test_provider_access_token_with_invalid_provider(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get(
                "/api/v1/oauth2/providers/invalid/authentication", headers=owner_auth_header
            )
            assert response.status_code == 404

    async def test_provider_access_token_with_not_found_code(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get(
                "/api/v1/oauth2/providers/huggingface/access-token", headers=owner_auth_header
            )
            assert response.status_code == 422
            assert response.json() == {"detail": "'code' parameter was not found in callback request"}

    async def test_provider_access_token_with_not_found_state(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get(
                "/api/v1/oauth2/providers/huggingface/access-token", params={"code": "code"}, headers=owner_auth_header
            )
            assert response.status_code == 422
            assert response.json() == {"detail": "'state' parameter was not found in callback request"}

    async def test_provider_access_token_with_invalid_state(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            response = await async_client.get(
                "/api/v1/oauth2/providers/huggingface/access-token",
                params={"code": "code", "state": "invalid"},
                headers=owner_auth_header,
                cookies={"oauth2_state": "valid"},
            )
            assert response.status_code == 422
            assert response.json() == {"detail": "'state' parameter does not match"}

    async def test_provider_access_token_with_authentication_error(
        self, async_client: AsyncClient, owner_auth_header: dict, default_oauth_settings: OAuth2Settings
    ):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            with mock.patch(
                "argilla_server.security.authentication.oauth2.providers.OAuth2ClientProvider._fetch_user_data",
                side_effect=AuthenticationError("error"),
            ):
                response = await async_client.get(
                    "/api/v1/oauth2/providers/huggingface/access-token",
                    params={"code": "code", "state": "valid"},
                    headers=owner_auth_header,
                    cookies={"oauth2_state": "valid"},
                )
                assert response.status_code == 401
                assert response.json() == {"detail": "error"}

    async def test_provider_access_token_with_already_created_user(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        owner_auth_header: dict,
        default_oauth_settings: OAuth2Settings,
    ):
        admin = await AdminFactory.create()

        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            with mock.patch(
                "argilla_server.security.authentication.oauth2.providers.OAuth2ClientProvider._fetch_user_data",
                return_value={"preferred_username": admin.username, "name": admin.first_name},
            ):
                response = await async_client.get(
                    "/api/v1/oauth2/providers/huggingface/access-token",
                    params={"code": "code", "state": "valid"},
                    headers=owner_auth_header,
                    cookies={"oauth2_state": "valid"},
                )
                assert response.status_code == 200

                userinfo = JWT.decode(response.json()["access_token"])
                assert userinfo["username"] == admin.username
                assert userinfo["role"] == admin.role

    async def test_provider_access_token_with_same_username(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        owner_auth_header: dict,
        default_oauth_settings: OAuth2Settings,
    ):
        user = await AnnotatorFactory.create()

        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=lambda: default_oauth_settings):
            with mock.patch(
                "argilla_server.security.authentication.oauth2.providers.OAuth2ClientProvider._fetch_user_data",
                return_value={"preferred_username": user.username, "name": user.first_name},
            ):
                response = await async_client.get(
                    "/api/v1/oauth2/providers/huggingface/access-token",
                    params={"code": "code", "state": "valid"},
                    headers=owner_auth_header,
                    cookies={"oauth2_state": "valid"},
                )
                # This will throw an error once we detect users created by OAuth2
                assert response.status_code == 200
