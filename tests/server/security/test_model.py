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
import uuid
from datetime import datetime

import pytest
from argilla.server.models import UserRole
from argilla.server.security.model import User, UserCreate, WorkspaceCreate
from pydantic import ValidationError


@pytest.mark.parametrize("wrong_name", ["user name", "user/name", "user.name", "UserName", "userName"])
def test_username_validator(wrong_name):
    with pytest.raises(ValidationError):
        UserCreate(username=wrong_name, password="12345678", first_name="Test")


@pytest.mark.parametrize("wrong_workspace", ["work space", "work/space", "work.space", "_", "-"])
def test_workspace_validator(wrong_workspace):
    with pytest.raises(ValidationError):
        WorkspaceCreate(name=wrong_workspace)


def test_workspaces_with_default():
    expected_workspaces = ["user", "ws1"]
    user = User(
        id=uuid.uuid4(),
        username="user",
        role=UserRole.annotator,
        workspaces=expected_workspaces,
        api_key="api-key",
        inserted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert len(user.workspaces) == len(expected_workspaces)
    for ws in expected_workspaces:
        assert ws in user.workspaces
