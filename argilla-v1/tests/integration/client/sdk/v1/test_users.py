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
from argilla_v1.client.sdk.v1.users.api import list_user_workspaces
from argilla_v1.client.sdk.v1.workspaces.models import WorkspaceModel
from argilla_v1.client.singleton import ArgillaSingleton

if TYPE_CHECKING:
    from argilla_server.models import User as ServerUser

from tests.factories import WorkspaceFactory, WorkspaceUserFactory


@pytest.mark.asyncio
async def test_list_user_workspaces(owner: "ServerUser") -> None:
    httpx_client = ArgillaSingleton.init(api_key=owner.api_key).http_client.httpx

    response = list_user_workspaces(client=httpx_client, user_id=owner.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    if len(response.parsed) > 0:
        assert all(isinstance(workspace, WorkspaceModel) for workspace in response.parsed)

    workspace = await WorkspaceFactory.create(name="test_workspace")
    await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=owner.id)

    response = list_user_workspaces(client=httpx_client, user_id=owner.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert any("test_workspace" == workspace.name for workspace in response.parsed)
