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

from uuid import uuid4

import pytest
from argilla.server.models import User, UserRole
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import UserFactory


def test_me(client: TestClient, admin: User, admin_auth_header: dict):
    response = client.get("/api/me", headers=admin_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert response_body["id"] == str(admin.id)


def test_me_without_authentication(client: TestClient):
    response = client.get("/api/me")

    assert response.status_code == 401


def test_list_users(client: TestClient, admin_auth_header: dict):
    UserFactory.create(username="username-a")
    UserFactory.create(username="username-b")

    response = client.get("/api/users", headers=admin_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert list(map(lambda user: user["username"], response_body)) == ["admin", "username-a", "username-b"]


def test_list_users_without_authentication(client: TestClient):
    response = client.get("/api/users")

    assert response.status_code == 401


def test_create_user(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 200
    assert db.query(User).count() == 2

    db_user = db.query(User).filter_by(username="username").first()
    assert db_user

    response_body = response.json()
    assert response_body["username"] == "username"
    assert response_body["api_key"] == db_user.api_key
    assert response_body["role"] == UserRole.annotator.value


def test_create_user_with_non_default_role(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "12345678", "role": UserRole.admin.value}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 200
    assert db.query(User).count() == 2

    db_user = db.query(User).filter_by(username="username").first()
    assert db_user

    response_body = response.json()
    assert response_body["username"] == "username"
    assert response_body["role"] == UserRole.admin.value


def test_create_user_without_authentication(client: TestClient, db: Session):
    user = {"first_name": "first-name", "username": "username", "password": "12345678"}

    response = client.post("/api/users", json=user)

    assert response.status_code == 401
    assert db.query(User).count() == 0


def test_create_user_with_invalid_min_length_first_name(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 422
    assert db.query(User).count() == 1


def test_create_user_with_invalid_min_length_last_name(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "first-name", "last_name": "", "username": "username", "password": "12345678"}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 422
    assert db.query(User).count() == 1


def test_create_user_with_invalid_username(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "first-name", "username": "invalid username", "password": "12345678"}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 422
    assert db.query(User).count() == 1


def test_create_user_with_invalid_role(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "12345678", "role": "invalid role"}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 422
    assert db.query(User).count() == 1


def test_create_user_with_invalid_min_password_length(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "1234"}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 422
    assert db.query(User).count() == 1


def test_create_user_with_invalid_max_password_length(client: TestClient, db: Session, admin_auth_header: dict):
    user = {"first_name": "first-name", "username": "username", "password": "p" * 101}

    response = client.post("/api/users", headers=admin_auth_header, json=user)

    assert response.status_code == 422
    assert db.query(User).count() == 1


def test_delete_user(client: TestClient, db: Session, admin_auth_header: dict):
    user = UserFactory.create()

    response = client.delete(f"/api/users/{user.id}", headers=admin_auth_header)

    assert response.status_code == 200
    assert db.query(User).count() == 1

    response_body = response.json()
    assert response_body["id"] == str(user.id)


def test_delete_user_without_authentication(client: TestClient, db: Session):
    user = UserFactory.create()

    response = client.delete(f"/api/users/{user.id}")

    assert response.status_code == 401
    assert db.query(User).count() == 1


def test_delete_user_with_nonexistent_user_id(client: TestClient, db: Session, admin_auth_header: dict):
    response = client.delete(f"/api/users/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.query(User).count() == 1
