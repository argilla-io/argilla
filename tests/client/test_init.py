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
from argilla.client import api
from argilla.client.api import active_api, active_client
from argilla.client.models import TextClassificationRecord
from argilla.server.models import User

from tests.factories import UserFactory, WorkspaceFactory


def test_resource_leaking_with_several_init(argilla_user: User):
    dataset = "test_resource_leaking_with_several_init"
    api.init(api_key=argilla_user.api_key)
    api.delete(dataset)

    # TODO: review performance in Windows. See https://github.com/recognai/argilla/pull/1702
    for i in range(0, 20):
        api.init(api_key=argilla_user.api_key)

    for i in range(0, 10):
        api.init(api_key=argilla_user.api_key)
        api.log(TextClassificationRecord(text="The text"), name=dataset, verbose=False)

    assert len(api.load(dataset)) == 10


def test_init_with_extra_headers(argilla_user: User):
    expected_headers = {
        "X-Custom-Header": "Mocking rules!",
        "Other-header": "Header value",
    }
    api.init(api_key=argilla_user.api_key, extra_headers=expected_headers)
    client = active_client()

    for key, value in expected_headers.items():
        assert client.http_client.headers[key] == value, f"{key}:{value} not in client headers"


def test_init(argilla_user: User):
    api.init(api_key=argilla_user.api_key)
    client = active_client()
    assert client.user.username == "argilla"

    api.init(api_key="argilla.apikey")
    client = active_api()
    assert client.user.username == "argilla"


@pytest.mark.asyncio
async def test_init_with_default_user_without_workspaces():
    argilla_user = await UserFactory.create(username="argilla")

    api.init(api_key=argilla_user.api_key)
    client = active_client()

    assert client.get_workspace() is None

    with pytest.raises(expected_exception=ValueError):
        client.set_workspace("argilla")


@pytest.mark.asyncio
async def test_init_with_default_user_and_different_workspace():
    workspace = await WorkspaceFactory.create()
    argilla_user = await UserFactory.create(username="argilla", workspaces=[workspace])

    api.init(api_key=argilla_user.api_key)
    client = active_client()

    assert client.get_workspace() is None

    client.set_workspace(workspace.name)
    assert client.get_workspace() == workspace.name
