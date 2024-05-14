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
from argilla_server._version import __version__ as version
from argilla_server.services.info import ApiInfo, ApiStatus

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_status(async_client: "AsyncClient"):
    response = await async_client.get("/api/_status")

    assert response.status_code == 200
    output = response.json()
    assert "version" in output and output["version"] == str(version)
    assert "elasticsearch" in output and isinstance(output["elasticsearch"], dict)
    assert "mem_info" in output and isinstance(output["mem_info"], dict)


@pytest.mark.asyncio
async def test_api_info(async_client: "AsyncClient"):
    response = await async_client.get("/api/_info")

    assert response.status_code == 200
    output = response.json()
    assert output["version"] == str(version)


@pytest.mark.asyncio
async def test_api_info(async_client: "AsyncClient"):
    response = await async_client.get("/api/_info")
    assert response.status_code == 200

    from argilla_server._version import __version__ as argilla_version

    info = ApiInfo.parse_obj(response.json())
    assert info.version == argilla_version


@pytest.mark.asyncio
async def test_api_status(async_client: "AsyncClient"):
    response = await async_client.get("/api/_status")
    assert response.status_code == 200

    from argilla_server._version import __version__ as argilla_version

    info = ApiStatus.parse_obj(response.json())
    assert info.version == argilla_version

    # Checking to not get the error dictionary service.py includes whenever something goes wrong
    assert "error" not in info.elasticsearch

    # Checking that the first key into mem_info dictionary has a nont-none value
    assert "rss" in info.mem_info is not None
