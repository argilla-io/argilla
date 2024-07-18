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
from typing import Union
from uuid import UUID

import pytest
from argilla_server.enums import QuestionType
from argilla_server.models import Question
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import DatasetFactory, SpanQuestionFactory, TextFieldFactory


@pytest.mark.asyncio
class TestCreateDatasetQuestion:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/questions"

    @pytest.mark.parametrize(
        "allow_overlapping,expected_allow_overlapping", [(None, False), (False, False), (True, True)]
    )
    async def test_create_dataset_span_question(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        owner_auth_header: dict,
        allow_overlapping: Union[bool, None],
        expected_allow_overlapping: bool,
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(name="field-a", dataset=dataset)

        settings = {
            "type": QuestionType.span,
            "field": "field-a",
            "visible_options": 3,
            "options": [
                {"value": "label-a", "text": "Label A", "description": "Label A description"},
                {"value": "label-b", "text": "Label B", "description": "Label B description"},
                {"value": "label-c", "text": "Label C", "description": "Label C description"},
            ],
        }

        if allow_overlapping is not None:
            settings["allow_overlapping"] = allow_overlapping

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"name": "name", "title": "Title", "description": "Description", "settings": settings},
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

        response_json = response.json()
        assert response_json == {
            "id": str(UUID(response_json["id"])),
            "name": "name",
            "title": "Title",
            "description": "Description",
            "required": False,
            "settings": {
                "type": QuestionType.span,
                "field": "field-a",
                "visible_options": 3,
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
                "allow_overlapping": expected_allow_overlapping,
                "allow_character_annotation": True,
            },
            "dataset_id": str(dataset.id),
            "inserted_at": datetime.fromisoformat(response_json["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_json["updated_at"]).isoformat(),
        }

    async def test_create_dataset_span_question_with_non_existent_field(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(name="field-a", dataset=dataset)
        await TextFieldFactory.create(name="field-b", dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "Title",
                "settings": {
                    "type": QuestionType.span,
                    "field": "field-non-existent",
                    "options": [
                        {"value": "label-a", "text": "Label A", "description": "Label A description"},
                        {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    ],
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "'field-non-existent' is not a valid field name.\nValid field names are ['field-a', 'field-b']"
        }

        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_other_span_question_using_the_same_field(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question = await SpanQuestionFactory(dataset=dataset)

        question_field = question.settings["field"]
        await TextFieldFactory.create(name=question_field, dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "new-question",
                "title": "Title",
                "settings": {
                    "type": QuestionType.span,
                    "field": question_field,
                    "options": [
                        {"value": "label-c", "text": "Label C", "description": "Label C description"},
                        {"value": "label-d", "text": "Label D", "description": "Label D description"},
                    ],
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": f"'field-a' is already used by span question with id '{question.id}'"}

    @pytest.mark.parametrize(
        "visible_options,error_msg",
        [
            (1, "ensure this value is greater than or equal to 3"),
            (4, "the value for 'visible_options' must be less or equal to the number of items in 'options' (3)"),
        ],
    )
    async def test_create_question_with_wrong_visible_options(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        owner_auth_header: dict,
        visible_options: int,
        error_msg: str,
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(name="field-a", dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "Title",
                "settings": {
                    "type": QuestionType.span,
                    "field": "field-a",
                    "visible_options": visible_options,
                    "options": [
                        {"value": "label-a", "text": "Label A", "description": "Label A description"},
                        {"value": "label-b", "text": "Label B", "description": "Label B description"},
                        {"value": "label-c", "text": "Label C", "description": "Label C description"},
                    ],
                },
            },
        )

        assert response.status_code == 422
        assert error_msg in response.text
