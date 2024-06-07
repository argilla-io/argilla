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
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGetVersion:
    def url(self) -> str:
        return "/api/v1/version"

    async def test_get_version(self, async_client: AsyncClient):
        response = await async_client.get(self.url())

        assert response.status_code == 200
        assert response.json() == {"version": __version__}
