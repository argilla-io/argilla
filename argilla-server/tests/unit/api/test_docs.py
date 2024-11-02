#  coding=utf-8
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
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_docs_redirect(async_client: "AsyncClient"):
    response = await async_client.get("/docs", follow_redirects=False)
    assert response.status_code == 307
    assert response.next_request.url.path == "/api/v1/docs"

    response = await async_client.get("/api", follow_redirects=False)
    assert response.status_code == 307
    assert response.next_request.url.path == "/api/v1/docs"
