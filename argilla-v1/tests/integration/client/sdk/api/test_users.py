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
from uuid import uuid4

import pytest
from argilla_v1.client.client import Argilla
from argilla_v1.client.sdk.client import AuthenticatedClient
from argilla_v1.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    BaseClientError,
    ForbiddenApiError,
    NotFoundApiError,
    UnauthorizedApiError,
    ValidationApiError,
)
from argilla_v1.client.sdk.users.api import create_user, delete_user, list_users, whoami
from argilla_v1.client.sdk.users.models import UserModel
from argilla_v1.client.singleton import ArgillaSingleton

from tests.factories import WorkspaceFactory

if TYPE_CHECKING:
    from argilla_server.models import User as ServerUser

from tests.factories import UserFactory


def test_whoami(api: Argilla) -> None:
    user = whoami(client=api.http_client)
    assert isinstance(user, UserModel)


def test_whoami_errors() -> None:
    with pytest.raises(
        BaseClientError, match="Your Api endpoint at http://localhost:6900 is not available or not responding"
    ):
        whoami(AuthenticatedClient(base_url="http://localhost:6900", token="wrong-apikey"))


@pytest.mark.asyncio
async def test_list_users(owner: "ServerUser") -> None:
    await UserFactory.create(username="user_1")
    await UserFactory.create(username="user_2")
    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = list_users(client=httpx_client)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert all(isinstance(user, UserModel) for user in response.parsed)
    assert all(user.username in ["user_1", "user_2", owner.username] for user in response.parsed)


@pytest.mark.parametrize("role", ["annotator", "admin", "owner"])
@pytest.mark.asyncio
async def test_create_user(owner: "ServerUser", role: str) -> None:
    await WorkspaceFactory.create(name="workspace_1")
    await WorkspaceFactory.create(name="workspace_2")

    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = create_user(
        client=httpx_client,
        first_name="user",
        username="user_1",
        password="user_password",
        role=role,
        workspaces=["workspace_1", "workspace_2"],
    )

    assert response.status_code == 200
    assert isinstance(response.parsed, UserModel)
    assert response.parsed.full_name == "user"
    assert response.parsed.username == "user_1"
    assert response.parsed.role == role
    assert response.parsed.workspaces == ["workspace_1", "workspace_2"]


def test_create_user_errors(owner: "ServerUser", annotator: "ServerUser") -> None:
    httpx_client = ArgillaSingleton.init(api_key=annotator.api_key).http_client.httpx
    with pytest.raises(ForbiddenApiError):
        create_user(
            client=httpx_client, first_name="user", username="user_1", password="user_password", role="annotator"
        )

    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx
    with pytest.raises(AlreadyExistsApiError):
        create_user(
            client=httpx_client,
            first_name="user",
            username=annotator.username,
            password="user_password",
            role="annotator",
        )

    with pytest.raises(ValidationApiError):
        create_user(
            client=httpx_client,
            first_name="another-user",
            username="another-user",
            password="user_password",
            role="annotator",
            workspaces=["i do not exist"],
        )


@pytest.mark.asyncio
async def test_delete_user(owner: "ServerUser") -> None:
    user = await UserFactory.create(username="user_1")
    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = delete_user(client=httpx_client, user_id=user.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, UserModel)


def test_delete_user_errors(owner: "ServerUser", annotator: "ServerUser") -> None:
    httpx_client = ArgillaSingleton.init(api_key=annotator.api_key).http_client.httpx
    with pytest.raises(ForbiddenApiError):
        delete_user(client=httpx_client, user_id=owner.id)

    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx
    with pytest.raises(NotFoundApiError):
        delete_user(client=httpx_client, user_id=str(uuid4()))

    delete_user(client=httpx_client, user_id=annotator.id)
    with pytest.raises(NotFoundApiError):
        delete_user(client=httpx_client, user_id=annotator.id)

    delete_user(client=httpx_client, user_id=owner.id)
    with pytest.raises(UnauthorizedApiError):
        delete_user(client=httpx_client, user_id=owner.id)
