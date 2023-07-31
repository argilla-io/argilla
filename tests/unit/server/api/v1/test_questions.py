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
from typing import TYPE_CHECKING, Type
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import DatasetStatus, Question
from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RatingQuestionFactory,
    TextQuestionFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from httpx import AsyncClient

    from tests.factories import QuestionFactory as QuestionFactoryType


@pytest.mark.parametrize(
    "QuestionFactory, expected_settings",
    [
        (TextQuestionFactory, {"type": "text", "use_markdown": False}),
        (
            RatingQuestionFactory,
            {
                "type": "rating",
                "options": [
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
        ),
        (
            LabelSelectionQuestionFactory,
            {
                "type": "label_selection",
                "options": [
                    {"value": "option1", "text": "Option 1", "description": None},
                    {"value": "option2", "text": "Option 2", "description": None},
                    {"value": "option3", "text": "Option 3", "description": None},
                ],
            },
        ),
        (
            MultiLabelSelectionQuestionFactory,
            {
                "type": "multi_label_selection",
                "options": [
                    {"value": "option1", "text": "Option 1", "description": None},
                    {"value": "option2", "text": "Option 2", "description": None},
                    {"value": "option3", "text": "Option 3", "description": None},
                ],
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_delete_question(
    async_client: "AsyncClient",
    db: "AsyncSession",
    owner_auth_header: dict,
    QuestionFactory: Type["QuestionFactoryType"],
    expected_settings: dict,
):
    question = await QuestionFactory.create(name="name", title="title", description="description")

    response = await async_client.delete(f"/api/v1/questions/{question.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    response_body = response.json()
    assert response_body == {
        "id": str(question.id),
        "name": "name",
        "title": "title",
        "description": "description",
        "required": False,
        "settings": expected_settings,
        "dataset_id": str(question.dataset_id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


@pytest.mark.asyncio
async def test_delete_question_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    question = await TextQuestionFactory.create()

    response = await async_client.delete(f"/api/v1/questions/{question.id}")

    assert response.status_code == 401
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_question_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    question = await TextQuestionFactory.create()

    response = await async_client.delete(
        f"/api/v1/questions/{question.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_question_belonging_to_published_dataset(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    dataset = await DatasetFactory.create(status=DatasetStatus.ready)
    question = await TextQuestionFactory.create(dataset=dataset)

    response = await async_client.delete(f"/api/v1/questions/{question.id}", headers=owner_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Questions cannot be deleted for a published dataset"}
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_question_with_nonexistent_question_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    await TextQuestionFactory.create()

    response = await async_client.delete(f"/api/v1/questions/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 1
