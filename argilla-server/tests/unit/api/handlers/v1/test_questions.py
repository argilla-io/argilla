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

from typing import TYPE_CHECKING, Type
from uuid import uuid4

import pytest
from argilla_server.api.schemas.v1.questions import (
    QUESTION_CREATE_DESCRIPTION_MAX_LENGTH,
    QUESTION_CREATE_TITLE_MAX_LENGTH,
)
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import OptionsOrder
from argilla_server.models import DatasetStatus, Question, UserRole
from sqlalchemy import func, select

from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    SpanQuestionFactory,
    TextQuestionFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from tests.factories import QuestionFactory as QuestionFactoryType


@pytest.mark.parametrize(
    "QuestionFactory, payload, expected_settings",
    [
        (
            TextQuestionFactory,
            {
                "title": "New Title",
                "description": "New Description",
                "settings": {"type": "text", "use_markdown": True},
            },
            {"type": "text", "use_markdown": True},
        ),
        (
            TextQuestionFactory,
            {"description": None, "settings": {"type": "text"}},
            {"type": "text", "use_markdown": False},
        ),
        (
            TextQuestionFactory,
            {"name": "New Name", "required": True, "dataset_id": str(uuid4()), "settings": {"type": "text"}},
            {"type": "text", "use_markdown": False},
        ),
        (
            RatingQuestionFactory,
            {"name": "New Name", "description": "New Description", "settings": {"type": "rating"}},
            {
                "type": "rating",
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
        ),
        (
            LabelSelectionQuestionFactory,
            {"settings": {"type": "label_selection", "visible_options": 3}},
            {
                "type": "label_selection",
                "options": [
                    {"value": "option1", "text": "Option 1", "description": None},
                    {"value": "option2", "text": "Option 2", "description": None},
                    {"value": "option3", "text": "Option 3", "description": None},
                ],
                "visible_options": 3,
            },
        ),
        (
            MultiLabelSelectionQuestionFactory,
            {
                "settings": {
                    "type": "multi_label_selection",
                    "visible_options": 3,
                },
            },
            {
                "type": "multi_label_selection",
                "options": [
                    {"value": "option1", "text": "Option 1", "description": None},
                    {"value": "option2", "text": "Option 2", "description": None},
                    {"value": "option3", "text": "Option 3", "description": None},
                ],
                "visible_options": 3,
                "options_order": OptionsOrder.natural,
            },
        ),
        (
            MultiLabelSelectionQuestionFactory,
            {
                "settings": {
                    "type": "multi_label_selection",
                    "options": [
                        {"value": "option3", "text": "Option 3", "description": None},
                        {"value": "option1", "text": "Option 1", "description": None},
                        {"value": "option2", "text": "Option 2", "description": None},
                    ],
                    "visible_options": None,
                }
            },
            {
                "type": "multi_label_selection",
                "options": [
                    {"value": "option3", "text": "Option 3", "description": None},
                    {"value": "option1", "text": "Option 1", "description": None},
                    {"value": "option2", "text": "Option 2", "description": None},
                ],
                "visible_options": None,
                "options_order": OptionsOrder.natural,
            },
        ),
        (
            LabelSelectionQuestionFactory,
            {"settings": {"type": "label_selection", "visible_options": None}},
            {
                "type": "label_selection",
                "options": [
                    {"value": "option1", "text": "Option 1", "description": None},
                    {"value": "option2", "text": "Option 2", "description": None},
                    {"value": "option3", "text": "Option 3", "description": None},
                ],
                "visible_options": None,
            },
        ),
        (
            LabelSelectionQuestionFactory,
            {
                "settings": {
                    "type": "label_selection",
                    "visible_options": None,
                    "options": [
                        {"value": "option3", "text": "Option 3", "description": None},
                        {"value": "option2", "text": "Option 2", "description": None},
                        {"value": "option1", "text": "Option 1", "description": None},
                    ],
                }
            },
            {
                "type": "label_selection",
                "visible_options": None,
                "options": [
                    {"value": "option3", "text": "Option 3", "description": None},
                    {"value": "option2", "text": "Option 2", "description": None},
                    {"value": "option1", "text": "Option 1", "description": None},
                ],
            },
        ),
        (
            RankingQuestionFactory,
            {"name": "New Name", "description": "New Description", "settings": {"type": "ranking"}},
            {
                "type": "ranking",
                "options": [
                    {"value": "completion-a", "text": "Completion A", "description": None},
                    {"value": "completion-b", "text": "Completion B", "description": None},
                    {"value": "completion-c", "text": "Completion C", "description": None},
                ],
            },
        ),
        (
            SpanQuestionFactory,
            {
                "settings": {
                    "type": "span",
                    "field": "field-a",
                    "options": [
                        {"value": "label-b", "text": "Label B", "description": "Label B description"},
                        {"value": "label-a", "text": "Label A", "description": "Label A description"},
                        {"value": "label-c", "text": "Label C", "description": "Label C description"},
                    ],
                }
            },
            {
                "type": "span",
                "field": "field-a",
                "options": [
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
                "allow_overlapping": False,
                "allow_character_annotation": True,
                "visible_options": None,
            },
        ),
        (
            SpanQuestionFactory,
            {
                "settings": {
                    "type": "span",
                    "visible_options": 3,
                }
            },
            {
                "type": "span",
                "field": "field-a",
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
                "allow_overlapping": False,
                "allow_character_annotation": True,
                "visible_options": 3,
            },
        ),
    ],
)
@pytest.mark.parametrize("role", [UserRole.owner])
@pytest.mark.asyncio
async def test_update_question(
    async_client: "AsyncClient",
    db: "AsyncSession",
    QuestionFactory: Type["QuestionFactoryType"],
    payload: dict,
    expected_settings: dict,
    role: UserRole,
):
    question = await QuestionFactory.create()
    user = await UserFactory.create(role=role, workspaces=[question.dataset.workspace])

    response = await async_client.patch(
        f"/api/v1/questions/{question.id}", headers={API_KEY_HEADER_NAME: user.api_key}, json=payload
    )

    title = payload.get("title") or question.title
    description = payload.get("description") or question.description

    assert response.status_code == 200, response.json()
    assert response.json() == {
        "id": str(question.id),
        "name": question.name,
        "title": title,
        "description": description,
        "required": False,
        "settings": expected_settings,
        "dataset_id": str(question.dataset_id),
        "inserted_at": question.inserted_at.isoformat(),
        "updated_at": question.updated_at.isoformat(),
    }

    question = await db.get(Question, question.id)

    assert question.title == title
    assert question.description == description
    assert question.settings == expected_settings


@pytest.mark.parametrize("title", [None, "", "t" * (QUESTION_CREATE_TITLE_MAX_LENGTH + 1)])
@pytest.mark.asyncio
async def test_update_question_with_invalid_title(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, title: str
):
    question = await TextQuestionFactory.create(title="title")

    response = await async_client.patch(
        f"/api/v1/questions/{question.id}", headers=owner_auth_header, json={"title": title}
    )

    assert response.status_code == 422

    question = await db.get(Question, question.id)
    assert question.title == "title"


@pytest.mark.asyncio
async def test_update_question_with_description_as_none(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    question = await TextQuestionFactory.create(description="description")

    response = await async_client.patch(
        f"/api/v1/questions/{question.id}", headers=owner_auth_header, json={"description": None}
    )

    assert response.status_code == 200
    assert response.json()["description"] == None

    question = await db.get(Question, question.id)
    assert question.description == None


@pytest.mark.parametrize("description", ["", "d" * (QUESTION_CREATE_DESCRIPTION_MAX_LENGTH + 1)])
@pytest.mark.asyncio
async def test_update_question_with_invalid_description(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, description: str
):
    question = await TextQuestionFactory.create(description="description")

    response = await async_client.patch(
        f"/api/v1/questions/{question.id}", headers=owner_auth_header, json={"description": description}
    )

    assert response.status_code == 422

    question = await db.get(Question, question.id)
    assert question.description == "description"


@pytest.mark.parametrize(
    "QuestionFactory, payload",
    [
        (TextQuestionFactory, {"settings": None}),
        (TextQuestionFactory, {"title": None, "description": None, "settings": None}),
        (TextQuestionFactory, {"settings": {"type": "text", "use_markdown": None}}),
        (TextQuestionFactory, {"title": "New Title", "settings": {"type": "label_selection"}}),
        (LabelSelectionQuestionFactory, {"settings": {"type": "label_selection", "visible_options": -5}}),
        (
            LabelSelectionQuestionFactory,
            {
                "settings": {
                    "type": "label_selection",
                    "options": [{"value": "undefined-option", "text": "Undefined option"}],
                }
            },
        ),
        (
            LabelSelectionQuestionFactory,
            {
                "settings": {
                    "type": "label_selection",
                    "options": [
                        {"value": "undefined-option-01", "text": "Undefined option"},
                        {"value": "undefined-option-02", "text": "Undefined option"},
                        {"value": "undefined-option-03", "text": "Undefined option"},
                    ],
                }
            },
        ),
        (MultiLabelSelectionQuestionFactory, {"settings": {"type": "multi_label_selection", "visible_options": -5}}),
        (
            MultiLabelSelectionQuestionFactory,
            {
                "settings": {
                    "type": "multi_label_selection",
                    "options": [{"value": "undefined-option", "text": "Undefined option"}],
                }
            },
        ),
        (
            MultiLabelSelectionQuestionFactory,
            {
                "settings": {
                    "type": "multi_label_selection",
                    "options": [
                        {"value": "undefined-option-01", "text": "Undefined option"},
                        {"value": "undefined-option-02", "text": "Undefined option"},
                        {"value": "undefined-option-03", "text": "Undefined option"},
                    ],
                }
            },
        ),
        (
            SpanQuestionFactory,
            {
                "settings": {
                    "type": "span",
                    "field": "field-a",
                    "options": [
                        {"value": "label-b", "text": "Label B", "description": "Label B description"},
                        {"value": "label-c", "text": "Label C", "description": "Label C description"},
                    ],
                }
            },
        ),
        (
            SpanQuestionFactory,
            {
                "settings": {
                    "type": "span",
                    "field": "field-a",
                    "options": [
                        {"value": "label-a", "text": "Label A", "description": "Label A description"},
                        {"value": "label-b", "text": "Label B", "description": "Label B description"},
                        {"value": "label-d", "text": "Label D", "description": "Label D description"},
                    ],
                }
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_question_with_invalid_settings(
    async_client: "AsyncClient", owner_auth_header: dict, QuestionFactory: Type["QuestionFactoryType"], payload: dict
):
    question = await QuestionFactory.create()

    response = await async_client.patch(f"/api/v1/questions/{question.id}", headers=owner_auth_header, json=payload)

    assert response.status_code == 422, payload


@pytest.mark.asyncio
async def test_update_question_with_invalid_payload(async_client: "AsyncClient", owner_auth_header: dict):
    question = await TextQuestionFactory.create()

    response = await async_client.patch(
        f"/api/v1/questions/{question.id}",
        headers=owner_auth_header,
        json={"title": {"this": "is", "not": "valid"}, "settings": {"use_markdown": "no"}},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_question_non_existent(async_client: "AsyncClient", owner_auth_header: dict):
    question_id = uuid4()

    response = await async_client.patch(
        f"/api/v1/questions/{question_id}",
        headers=owner_auth_header,
        json={"title": "New Title", "settings": {"type": "text", "use_markdown": True}},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Question with id `{question_id}` not found"}


@pytest.mark.asyncio
async def test_update_question_as_admin_from_different_workspace(async_client: "AsyncClient"):
    question = await TextQuestionFactory.create()
    user = await UserFactory.create(role=UserRole.admin)

    response = await async_client.patch(
        f"/api/v1/questions/{question.id}",
        headers={API_KEY_HEADER_NAME: user.api_key},
        json={"title": "New Title", "settings": {"type": "text", "use_markdown": True}},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_question_as_annotator(async_client: "AsyncClient"):
    question = await TextQuestionFactory.create()
    user = await AnnotatorFactory.create(workspaces=[question.dataset.workspace])

    response = await async_client.patch(
        f"/api/v1/questions/{question.id}",
        headers={API_KEY_HEADER_NAME: user.api_key},
        json={"title": "New Title", "settings": {"type": "text", "use_markdown": True}},
    )

    assert response.status_code == 403


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete_question(async_client: "AsyncClient", db: "AsyncSession", role: UserRole):
    question = await TextQuestionFactory.create(name="name", title="title", description="description")
    user = await UserFactory.create(role=role, workspaces=[question.dataset.workspace])

    response = await async_client.delete(
        f"/api/v1/questions/{question.id}", headers={API_KEY_HEADER_NAME: user.api_key}
    )

    assert response.status_code == 200
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    response_body = response.json()
    assert response_body == {
        "id": str(question.id),
        "name": "name",
        "title": "title",
        "description": "description",
        "required": False,
        "settings": {"type": "text", "use_markdown": False},
        "dataset_id": str(question.dataset_id),
        "inserted_at": question.inserted_at.isoformat(),
        "updated_at": question.updated_at.isoformat(),
    }


@pytest.mark.asyncio
async def test_delete_question_as_admin_from_different_workspace(async_client: "AsyncClient", db: "AsyncSession"):
    user = await UserFactory.create(role=UserRole.admin)
    question = await TextQuestionFactory.create()

    response = await async_client.delete(
        f"/api/v1/questions/{question.id}", headers={API_KEY_HEADER_NAME: user.api_key}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 1


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
    assert response.json() == {"detail": "questions cannot be deleted for a published dataset"}
    assert (await db.execute(select(func.count(Question.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_question_with_nonexistent_question_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    question_id = uuid4()

    await TextQuestionFactory.create()

    response = await async_client.delete(
        f"/api/v1/questions/{question_id}",
        headers=owner_auth_header,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Question with id `{question_id}` not found"}

    assert (await db.execute(select(func.count(Question.id)))).scalar() == 1
