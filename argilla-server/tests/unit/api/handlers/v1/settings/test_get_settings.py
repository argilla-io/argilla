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
from unittest import mock

import pytest
from argilla_server.contexts import settings as settings_context
from argilla_server.contexts.settings import HUGGINGFACE_SETTINGS
from argilla_server.integrations.huggingface.spaces import HuggingfaceSettings
from argilla_server.settings import settings as argilla_server_settings, settings
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGetSettings:
    def url(self) -> str:
        return "/api/v1/settings"

    async def test_get_settings_for_argilla_settings_running_on_huggingface(self, async_client: AsyncClient):
        with mock.patch.object(HUGGINGFACE_SETTINGS, "space_id", "space-id"):
            response = await async_client.get(self.url())

            assert response.status_code == 200
            assert response.json()["argilla"]["show_huggingface_space_persistent_storage_warning"] is True

    async def test_get_settings_for_argilla_settings_running_on_huggingface_with_disabled_storage_warning(
        self, async_client: AsyncClient
    ):
        with mock.patch.object(HUGGINGFACE_SETTINGS, "space_id", "space-id"):
            with mock.patch.object(argilla_server_settings, "show_huggingface_space_persistent_storage_warning", False):
                response = await async_client.get(self.url())

                assert response.status_code == 200
                assert response.json()["argilla"]["show_huggingface_space_persistent_storage_warning"] is False

    async def test_get_settings_for_argilla_settings_not_running_on_huggingface(self, async_client: AsyncClient):
        response = await async_client.get(self.url())

        assert response.status_code == 200
        assert "show_huggingface_space_persistent_storage_warning" not in response.json()["argilla"]

    async def test_get_settings_for_huggingface_settings_running_on_huggingface(self, async_client: AsyncClient):
        huggingface_os_environ = {
            "SPACE_ID": "space-id",
            "SPACE_TITLE": "space-title",
            "SPACE_SUBDOMAIN": "space-subdomain",
            "SPACE_HOST": "space-host",
            "SPACE_REPO_NAME": "space-repo-name",
            "SPACE_AUTHOR_NAME": "space-author-name",
            "PERSISTANT_STORAGE_ENABLED": "true",
        }

        with mock.patch.dict(os.environ, huggingface_os_environ):
            with mock.patch.object(settings_context, "HUGGINGFACE_SETTINGS", HuggingfaceSettings()):
                response = await async_client.get(self.url())

                assert response.status_code == 200
                assert response.json()["huggingface"] == {
                    "space_id": "space-id",
                    "space_title": "space-title",
                    "space_subdomain": "space-subdomain",
                    "space_host": "space-host",
                    "space_repo_name": "space-repo-name",
                    "space_author_name": "space-author-name",
                    "space_persistent_storage_enabled": True,
                }

    async def test_get_settings_for_huggingface_settings_not_running_on_huggingface(self, async_client: AsyncClient):
        response = await async_client.get(self.url())

        assert response.status_code == 200
        assert "huggingface" not in response.json()

    async def test_get_settings_with_share_your_progress_enabled(self, async_client: AsyncClient):
        try:
            settings.enable_share_your_progress = True

            response = await async_client.get(self.url())

            assert response.status_code == 200
            assert response.json()["argilla"]["share_your_progress_enabled"] is True
        finally:
            settings.enable_share_your_progress = False
