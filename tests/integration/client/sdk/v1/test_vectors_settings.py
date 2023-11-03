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
from argilla.client import api
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.vectors_settings.api import update_vector_settings
from argilla.client.users import User
from argilla.client.workspaces import Workspace

if TYPE_CHECKING:
    from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
    from argilla.server.models.database import User as ServerUser


@pytest.mark.asyncio
class TestVectorsSettingsSDK:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_update_vectors_settings(
        self, owner: "ServerUser", role: UserRole, feedback_dataset: "FeedbackDataset"
    ) -> None:
        api.init(api_key=owner.api_key)

        user = User.create(username="test-user", password="test-password", role=role)
        workspace = Workspace.create("test-workspace")
        workspace.add_user(user.id)

        api.init(api_key=user.api_key)

        remote = feedback_dataset.push_to_argilla(name="test-dataset", workspace=workspace)

        client = api.active_client()

        vector_settings = remote.vectors_settings[0]

        response = update_vector_settings(
            client=client.client.httpx, id=vector_settings.id, title="New title for vectors settings"
        )

        updated_vector_settings = remote.vectors_settings[0]
        assert updated_vector_settings.title  == "New title for vectors settings"
