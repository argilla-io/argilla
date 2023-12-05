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
from argilla.server.enums import SuggestionType
from httpx import AsyncClient

from tests.factories import RecordFactory, TextQuestionFactory


@pytest.mark.asyncio
class TestUpsertSuggestion:
    def url(self, record_id: UUID) -> str:
        return f"/api/v1/records/{record_id}/suggestions"

    @pytest.mark.parametrize(
        "agent", ["a", "A", "0", "gpt 3.5", "gpt-3.5-turbo", "argilla/zephyr-7b", "ft:gpt-3.5-turbo"]
    )
    async def test_with_valid_agent(self, async_client: AsyncClient, owner_auth_header: dict, agent: str):
        record = await RecordFactory.create()
        question = await TextQuestionFactory.create(dataset=record.dataset)

        response = await async_client.put(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "question_id": str(question.id),
                "type": SuggestionType.model,
                "value": "value",
                "agent": agent,
                "score": 1.0,
            },
        )

        assert response.status_code == 201

    @pytest.mark.parametrize("agent", ["", " ", "  ", "-", "_", ":", ".", "/", ","])
    async def test_with_invalid_agent(self, async_client: AsyncClient, owner_auth_header: dict, agent: str):
        response = await async_client.put(
            self.url(uuid4()),
            headers=owner_auth_header,
            json={
                "question_id": str(uuid4()),
                "type": SuggestionType.model,
                "value": "value",
                "agent": agent,
                "score": 1.0,
            },
        )

        assert response.status_code == 422

    async def test_with_invalid_min_length_agent(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.put(
            self.url(uuid4()),
            headers=owner_auth_header,
            json={
                "question_id": str(uuid4()),
                "type": SuggestionType.model,
                "value": "value",
                "agent": "",
                "score": 1.0,
            },
        )

        assert response.status_code == 422

    async def test_with_invalid_max_length_agent(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.put(
            self.url(uuid4()),
            headers=owner_auth_header,
            json={
                "question_id": str(uuid4()),
                "type": SuggestionType.model,
                "value": "value",
                "agent": "a" * 201,
                "score": 1.0,
            },
        )

        assert response.status_code == 422

    async def test_with_invalid_lower_score(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.put(
            self.url(uuid4()),
            headers=owner_auth_header,
            json={
                "question_id": str(uuid4()),
                "type": SuggestionType.model,
                "value": "value",
                "agent": "agent",
                "score": -0.1,
            },
        )

        assert response.status_code == 422

    async def test_with_invalid_upper_score(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.put(
            self.url(uuid4()),
            headers=owner_auth_header,
            json={
                "question_id": str(uuid4()),
                "type": SuggestionType.model,
                "value": "value",
                "agent": "agent",
                "score": 1.1,
            },
        )

        assert response.status_code == 422
