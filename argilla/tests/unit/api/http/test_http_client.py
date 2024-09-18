# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import MagicMock, patch

import pytest
from argilla import Argilla
from httpx import Timeout


class TestHTTPClient:
    def test_create_default_client(self):
        http_client = Argilla().http_client

        assert http_client is not None
        assert http_client.base_url == "http://localhost:6900"
        assert http_client.timeout == Timeout(60)
        assert http_client.headers["X-Argilla-Api-Key"] == "argilla.apikey"

    def test_create_client_with_custom_timeout(self):
        http_client = Argilla(timeout=30).http_client

        assert http_client is not None
        assert http_client.base_url == "http://localhost:6900"
        assert http_client.timeout == Timeout(30)
        assert http_client.headers["X-Argilla-Api-Key"] == "argilla.apikey"

    def test_create_client_with_custom_api_url(self):
        http_client = Argilla(api_url="http://localhost:8000").http_client

        assert http_client is not None
        assert http_client.base_url == "http://localhost:8000"

    def test_create_client_with_custom_api_key(self):
        http_client = Argilla(api_key="custom.apikey").http_client

        assert http_client is not None
        assert http_client.base_url == "http://localhost:6900"
        assert http_client.headers["X-Argilla-Api-Key"] == "custom.apikey"

    def test_create_client_with_extra_headers(self):
        http_client = Argilla(headers={"X-Custom-Header": "Custom value"}).http_client

        assert http_client is not None
        assert http_client.base_url == "http://localhost:6900"
        assert http_client.headers["X-Argilla-Api-Key"] == "argilla.apikey"
        assert http_client.headers["X-Custom-Header"] == "Custom value"

    def test_create_client_with_extra_cookies(self):
        http_client = Argilla(cookies={"session": "session_id"}).http_client

        assert http_client is not None
        assert http_client.base_url == "http://localhost:6900"
        assert http_client.headers["X-Argilla-Api-Key"] == "argilla.apikey"
        assert http_client.cookies["session"] == "session_id"

    @pytest.mark.parametrize("retries", [0, 1, 5, 10])
    def test_create_client_with_various_retries(self, retries):
        with patch("argilla._api._client.create_http_client") as mock_create_http_client:
            mock_http_client = MagicMock()
            mock_create_http_client.return_value = mock_http_client

            Argilla(api_url="http://test.com", api_key="test_key", retries=retries)

            mock_create_http_client.assert_called_once_with(
                api_url="http://test.com", api_key="test_key", timeout=60, retries=retries
            )
