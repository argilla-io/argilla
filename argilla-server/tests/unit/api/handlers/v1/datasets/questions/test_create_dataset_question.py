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
from argilla_server.models import Question
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import DatasetFactory


@pytest.mark.asyncio
class TestCreateDatasetQuestion:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/questions"

    async def test_create_dataset_multi_label_selection_question_with_options_order(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {
                    "type": QuestionType.multi_label_selection,
                    "options": [
                        {"value": "label-a", "text": "Label A"},
                        {"value": "label-b", "text": "Label B"},
                    ],
                    "options_order": OptionsOrder.suggestion,
                },
            },
        )

        assert response.status_code == 201

        response_json = response.json()
        assert response_json["settings"]["options_order"] == OptionsOrder.suggestion

        question = (await db.execute(select(Question).filter_by(id=UUID(response_json["id"])))).scalar_one()
        assert question.settings["options_order"] == OptionsOrder.suggestion

    async def test_create_dataset_multi_label_selection_question_without_options_order(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {
                    "type": QuestionType.multi_label_selection,
                    "options": [
                        {"value": "label-a", "text": "Label A"},
                        {"value": "label-b", "text": "Label B"},
                    ],
                },
            },
        )

        assert response.status_code == 201

        response_json = response.json()
        assert response_json["settings"]["options_order"] == OptionsOrder.natural

        question = (await db.execute(select(Question).filter_by(id=UUID(response_json["id"])))).scalar_one()
        assert question.settings["options_order"] == OptionsOrder.natural

    async def test_create_dataset_multi_label_selection_question_with_options_order_as_none(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {
                    "type": QuestionType.multi_label_selection,
                    "options": [
                        {"value": "label-a", "text": "Label A"},
                        {"value": "label-b", "text": "Label B"},
                    ],
                    "options_order": None,
                },
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar_one() == 0

    async def test_create_dataset_rating_question(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {
                    "type": QuestionType.rating,
                    "options": [
                        {"value": 0},
                        {"value": 1},
                        {"value": 2},
                        {"value": 3},
                        {"value": 4},
                        {"value": 5},
                        {"value": 6},
                        {"value": 7},
                        {"value": 8},
                        {"value": 9},
                        {"value": 10},
                    ],
                },
            },
        )

        question = (await db.execute(select(Question))).scalar_one()

        assert response.status_code == 201
        assert response.json() == {
            "id": str(question.id),
            "name": "name",
            "title": "title",
            "description": None,
            "required": False,
            "settings": {
                "type": QuestionType.rating,
                "options": [
                    {"value": 0},
                    {"value": 1},
                    {"value": 2},
                    {"value": 3},
                    {"value": 4},
                    {"value": 5},
                    {"value": 6},
                    {"value": 7},
                    {"value": 8},
                    {"value": 9},
                    {"value": 10},
                ],
            },
            "dataset_id": str(dataset.id),
            "inserted_at": question.inserted_at.isoformat(),
            "updated_at": question.updated_at.isoformat(),
        }
