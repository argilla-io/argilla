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

import pytest
from argilla.client import api
from argilla.client.workspaces import Workspace


def test_workspace_cls_init(mocked_client):
    the_api = api.active_api()
    workspace = the_api.http_client.post("/api/workspaces", json={"name": "test_workspace"})
    assert workspace["name"] == "test_workspace"

    api.init(api_key="argilla.apikey")
    workspace = Workspace.from_name("test_workspace")
    assert workspace.name == "test_workspace"
    assert isinstance(workspace.id, str)

    with pytest.raises(ValueError):
        Workspace.from_name("this_workspace_does_not_exist")
