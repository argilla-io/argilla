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
@pytest.mark.parametrize("not_found_endpoint", ["/api/not/found/route", "/api/v1/not-found", "/api/v2/not-found"])
async def test_route_not_found_response(async_client: AsyncClient, http_method: str, not_found_endpoint: str):
    response = await async_client.request(method=http_method, url=not_found_endpoint)

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
