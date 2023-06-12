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
from argilla.server.models import User

from tests.factories import WorkspaceFactory, WorkspaceUserFactory


def test_workspace_cls_init(argilla_user: User):
    workspace = WorkspaceFactory.create()
    WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=argilla_user.id)

    api.init(api_key=argilla_user.api_key)
    found_workspace = Workspace.from_name(workspace.name)

    assert found_workspace.name == workspace.name
    assert isinstance(found_workspace.id, str)

    with pytest.raises(ValueError):
        Workspace.from_name("this_workspace_does_not_exist")
