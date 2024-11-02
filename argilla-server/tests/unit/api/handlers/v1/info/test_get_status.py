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
from argilla_server._version import __version__
from argilla_server.search_engine import SearchEngine
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGetStatus:
    def url(self) -> str:
        return "/api/v1/status"

    async def test_get_status(self, async_client: AsyncClient, mock_search_engine: SearchEngine):
        mock_search_engine.info.return_value = {}

        response = await async_client.get(self.url())

        assert response.status_code == 200

        response_json = response.json()
        assert response_json["version"] == __version__
        assert "search_engine" in response_json
        assert "memory" in response_json
