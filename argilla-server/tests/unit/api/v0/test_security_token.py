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
from argilla_server.models import User
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_create_security_token(async_client: "AsyncClient", owner):
    response = await async_client.post("/api/security/token", data={"username": owner.username, "password": "1234"})

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["access_token"]
    assert response_body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_create_security_token_with_empty_username(async_client: "AsyncClient"):
    response = await async_client.post("/api/security/token", data={"username": "", "password": "1234"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_security_token_with_empty_password(async_client: "AsyncClient", owner):
    response = await async_client.post("/api/security/token", data={"username": owner.username, "password": ""})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_security_token_with_invalid_username(async_client: "AsyncClient"):
    response = await async_client.post("/api/security/token", data={"username": "invalid", "password": "1234"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_security_token_with_invalid_password(async_client: "AsyncClient", owner):
    response = await async_client.post("/api/security/token", data={"username": owner.username, "password": "invalid"})

    assert response.status_code == 401
