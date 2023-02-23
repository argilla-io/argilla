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

from argilla.server.models import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_security_token(client: TestClient, admin: User):
    response = client.post("/api/security/token", data={"username": admin.username, "password": "1234"})

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["access_token"]
    assert response_body["token_type"] == "bearer"


def test_create_security_token_with_empty_username(client: TestClient):
    response = client.post("/api/security/token", data={"username": "", "password": "1234"})

    assert response.status_code == 422


def test_create_security_token_with_empty_password(client: TestClient, admin: User):
    response = client.post("/api/security/token", data={"username": admin.username, "password": ""})

    assert response.status_code == 422


def test_create_security_token_with_invalid_username(client: TestClient):
    response = client.post("/api/security/token", data={"username": "invalid", "password": "1234"})

    assert response.status_code == 401


def test_create_security_token_with_invalid_password(client: TestClient, admin: User):
    response = client.post("/api/security/token", data={"username": admin.username, "password": "invalid"})

    assert response.status_code == 401
