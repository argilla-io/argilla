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
from argilla_v1.client.sdk.users.models import UserModel
from argilla_v1.client.sdk.workspaces.api import (
    create_workspace,
    create_workspace_user,
    delete_workspace_user,
    list_workspace_users,
)
from argilla_v1.client.sdk.workspaces.models import WorkspaceModel
from argilla_v1.client.singleton import ArgillaSingleton

from tests.factories import WorkspaceFactory, WorkspaceUserFactory


def test_create_workspace(owner: User) -> None:
    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = create_workspace(client=httpx_client, name="test_workspace")
    assert response.status_code == 200
    assert isinstance(response.parsed, WorkspaceModel)
    assert response.parsed.name == "test_workspace"


@pytest.mark.asyncio
async def test_list_workspace_users(owner: User) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)
    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = list_workspace_users(client=httpx_client, id=workspace.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], UserModel)


@pytest.mark.asyncio
async def test_create_workspace_user(owner: User) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = create_workspace_user(client=httpx_client, id=workspace.id, user_id=owner.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, UserModel)
    assert response.parsed.id == owner.id
    assert response.parsed.workspaces[0] == workspace.name


@pytest.mark.asyncio
async def test_delete_workspace_user(owner: User) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)
    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = delete_workspace_user(client=httpx_client, id=workspace.id, user_id=owner.id)
    assert response.status_code == 200
    assert response.parsed.workspaces == []
