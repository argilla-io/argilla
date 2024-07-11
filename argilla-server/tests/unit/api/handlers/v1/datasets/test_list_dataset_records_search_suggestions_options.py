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

from uuid import UUID, uuid4

import pytest
from argilla_server.constants import API_KEY_HEADER_NAME
from httpx import AsyncClient

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    OwnerFactory,
    QuestionFactory,
    SuggestionFactory,
)


@pytest.mark.asyncio
class TestListDatasetRecordsSearchSuggestionsOptions:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/search/suggestions/options"

    async def test(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        question_a = await QuestionFactory.create(name="question-a", dataset=dataset)
        question_b = await QuestionFactory.create(name="question-b", dataset=dataset)
        question_c = await QuestionFactory.create(name="question-c", dataset=dataset)

        await SuggestionFactory.create(question=question_a)
        await SuggestionFactory.create(question=question_b, agent="agent-a")
        await SuggestionFactory.create(question=question_b, agent="agent-a")
        await SuggestionFactory.create(question=question_c, agent="agent-a")
        await SuggestionFactory.create(question=question_c, agent="agent-b")
        await SuggestionFactory.create(question=question_c, agent="agent-c")
        await SuggestionFactory.create(question=question_c, agent="agent-c")

        extra_dataset = await DatasetFactory.create()
        extra_question_a = await QuestionFactory.create(name="extra-question-a", dataset=extra_dataset)
        extra_question_b = await QuestionFactory.create(name="extra-question-b", dataset=extra_dataset)

        await SuggestionFactory.create(question=extra_question_a, agent="extra-agent-a")
        await SuggestionFactory.create(question=extra_question_b, agent="extra-agent-b")

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "question": {
                        "id": str(question_a.id),
                        "name": "question-a",
                    },
                    "agents": [],
                },
                {
                    "question": {
                        "id": str(question_b.id),
                        "name": "question-b",
                    },
                    "agents": ["agent-a"],
                },
                {
                    "question": {
                        "id": str(question_c.id),
                        "name": "question-c",
                    },
                    "agents": ["agent-a", "agent-b", "agent-c"],
                },
            ]
        }

    async def test_with_dataset_without_questions(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {"items": []}

    async def test_with_dataset_without_suggestions(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        question_a = await QuestionFactory.create(name="question-a", dataset=dataset)
        question_b = await QuestionFactory.create(name="question-b", dataset=dataset)
        question_c = await QuestionFactory.create(name="question-c", dataset=dataset)

        extra_dataset = await DatasetFactory.create()
        extra_question_a = await QuestionFactory.create(name="extra-question-a", dataset=extra_dataset)
        extra_question_b = await QuestionFactory.create(name="extra-question-b", dataset=extra_dataset)

        await SuggestionFactory.create(question=extra_question_a, agent="extra-agent-a")
        await SuggestionFactory.create(question=extra_question_b, agent="extra-agent-b")

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "question": {
                        "id": str(question_a.id),
                        "name": question_a.name,
                    },
                    "agents": [],
                },
                {
                    "question": {
                        "id": str(question_b.id),
                        "name": question_b.name,
                    },
                    "agents": [],
                },
                {
                    "question": {
                        "id": str(question_c.id),
                        "name": question_c.name,
                    },
                    "agents": [],
                },
            ]
        }

    async def test_as_owner(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        owner = await OwnerFactory.create(workspaces=[dataset.workspace])

        response = await async_client.get(self.url(dataset.id), headers={API_KEY_HEADER_NAME: owner.api_key})

        assert response.status_code == 200

    async def test_as_admin(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        admin = await AdminFactory.create(workspaces=[dataset.workspace])

        response = await async_client.get(self.url(dataset.id), headers={API_KEY_HEADER_NAME: admin.api_key})

        assert response.status_code == 200

    async def test_as_annotator(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        response = await async_client.get(self.url(dataset.id), headers={API_KEY_HEADER_NAME: annotator.api_key})

        assert response.status_code == 200

    async def test_as_user_from_different_workspace(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        annotator = await AnnotatorFactory.create()

        response = await async_client.get(self.url(dataset.id), headers={API_KEY_HEADER_NAME: annotator.api_key})

        assert response.status_code == 403

    async def test_with_non_existent_dataset(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset_id = uuid4()

        response = await async_client.get(self.url(dataset_id), headers=owner_auth_header)

        assert response.status_code == 404
        assert response.json() == {"detail": f"Dataset with id `{dataset_id}` not found"}
