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

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import httpx
import pytest
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.workspaces.models import WorkspaceModel
from argilla.client.users import User

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def user(mocker: "MockerFixture") -> User:
    mocker.patch.object(
        User,
        "workspaces",
        new_callable=lambda: [
            WorkspaceModel(id=uuid4(), name="unit-test", inserted_at=datetime.now(), updated_at=datetime.now())
        ],
    )
    user = User.__new__(User)
    user.__dict__.update(
        {
            "_client": httpx.Client(),
            "id": uuid4(),
            "username": "unit-test",
            "last_name": "unit-test",
            "first_name": "unit-test",
            "role": UserRole.owner,
            "api_key": "apikey.unit-test",
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )
    return user
