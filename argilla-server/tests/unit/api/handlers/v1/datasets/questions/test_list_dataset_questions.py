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

from uuid import UUID

import pytest
from argilla_server.enums import OptionsOrder, QuestionType
from httpx import AsyncClient

from tests.factories import QuestionFactory


@pytest.mark.asyncio
class TestListDatasetQuestions:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/questions"

    async def test_list_dataset_multi_label_selection_question_with_options_order(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await QuestionFactory.create(
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                ],
                "options_order": OptionsOrder.suggestion,
            },
        )

        response = await async_client.get(self.url(question.dataset_id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json()["items"][0]["settings"]["options_order"] == OptionsOrder.suggestion
        assert question.settings["options_order"] == OptionsOrder.suggestion

    async def test_list_dataset_multi_label_selection_question_without_options_order(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await QuestionFactory.create(
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                ],
            },
        )

        response = await async_client.get(self.url(question.dataset_id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json()["items"][0]["settings"]["options_order"] == OptionsOrder.natural
        assert "options_order" not in question.settings
