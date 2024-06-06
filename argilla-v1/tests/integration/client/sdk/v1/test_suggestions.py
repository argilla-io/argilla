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
from argilla_server.models import UserRole
from argilla_v1.client.client import Argilla
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.questions import TextQuestion
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.sdk.v1.suggestions.api import delete_suggestion
from argilla_v1.client.singleton import init

from tests.factories import UserFactory, WorkspaceFactory


@pytest.mark.asyncio
class TestSuggestionsSDK:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_suggestions(self, role: UserRole) -> None:
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(role=role, workspaces=[workspace])

        init(api_key=user.api_key, workspace=workspace.name)

        dataset = FeedbackDataset(
            fields=[TextField(name="text-field")],
            questions=[TextQuestion(name="text-question")],
        )

        dataset.add_records(
            FeedbackRecord(
                fields={"text-field": "unit-test"},
                suggestions=[{"question_name": "text-question", "value": "suggestion"}],
            )
        )

        remote = dataset.push_to_argilla(name="test-dataset", workspace=workspace.name)

        suggestion_id = remote[0].suggestions[0].id

        api = Argilla(api_key=user.api_key, workspace=workspace.name)

        response = delete_suggestion(client=api.client.httpx, id=suggestion_id)
        assert response.status_code == 200
        assert response.parsed.id == suggestion_id
