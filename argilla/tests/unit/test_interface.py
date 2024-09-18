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

from unittest import mock

import argilla as rg


class TestArgilla:
    def test_default_client(self):
        with mock.patch("argilla.Argilla") as mock_client:
            mock_client.return_value.api_url = "http://localhost:6900"
            mock_client.return_value.api_key = "admin.apikey"
            mock_client.return_value.workspace = "argilla"

            client = rg.Argilla(api_url="http://localhost:6900", api_key="admin.apikey")
            assert client.api_url == "http://localhost:6900"
            assert client.api_key == "admin.apikey"

    def test_multiple_clients(self):
        local_client = rg.Argilla(api_url="http://localhost:6900", api_key="admin.apikey")
        remote_client = rg.Argilla(api_url="http://argilla.production.net", api_key="admin.apikey")

        assert local_client.api_url == "http://localhost:6900"
        assert remote_client.api_url == "http://argilla.production.net"
