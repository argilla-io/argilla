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
from argilla_v1.client.sdk.users.models import UserRole
from argilla_v1.client.sdk.v1.workspaces.api import get_workspace, list_workspaces_me
from argilla_v1.client.sdk.v1.workspaces.models import WorkspaceModel
from argilla_v1.client.singleton import ArgillaSingleton

from tests.factories import UserFactory, WorkspaceFactory


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
async def test_get_workspace(role: UserRole) -> None:
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace])

    httpx_client = ArgillaSingleton.init(api_key=user.api_key).http_client.httpx

    response = get_workspace(client=httpx_client, id=workspace.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, WorkspaceModel)
    assert response.parsed.id == workspace.id


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
async def test_list_workspaces_me(role: UserRole) -> None:
    workspaces = await WorkspaceFactory.create_batch(size=5)
    user = await UserFactory.create(role=role, workspaces=workspaces if role != UserRole.owner else [])

    httpx_client = ArgillaSingleton.init(api_key=user.api_key).http_client.httpx

    response = list_workspaces_me(client=httpx_client)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], WorkspaceModel)
    assert len(response.parsed) == len(workspaces)
