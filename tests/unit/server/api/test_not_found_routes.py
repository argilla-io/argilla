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
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize("http_method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
async def test_route_not_found_response(async_client: AsyncClient, http_method: str):
    response = await async_client.request(method=http_method, url="/api/not/found/route")

    assert response.status_code == 404
    assert response.json() == {"detail": "Endpoint '/api/not/found/route' not found"}
