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
from uuid import UUID, uuid4

import pytest
from argilla_server.api.schemas.v1.questions import (
    QUESTION_CREATE_DESCRIPTION_MAX_LENGTH,
    QUESTION_CREATE_NAME_MAX_LENGTH,
    QUESTION_CREATE_TITLE_MAX_LENGTH,
    RANKING_OPTIONS_MAX_ITEMS,
    RATING_OPTIONS_MAX_ITEMS,
    RATING_OPTIONS_MIN_ITEMS,
    VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH,
    VALUE_TEXT_OPTION_TEXT_MAX_LENGTH,
    VALUE_TEXT_OPTION_VALUE_MAX_LENGTH,
)
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import DatasetStatus
from argilla_server.models import Question
from argilla_server.settings import settings
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    QuestionFactory,
    TextFieldFactory,
    WorkspaceFactory,
)


@pytest.mark.asyncio
class TestDatasetQuestions:
    @pytest.mark.parametrize(
        ("settings", "expected_settings"),
        [
            ({"type": "text"}, {"type": "text", "use_markdown": False}),
            ({"type": "text", "use_markdown": True}, {"type": "text", "use_markdown": True}),
            ({"type": "text", "use_markdown": False}, {"type": "text", "use_markdown": False}),
            (
                {
                    "type": "rating",
                    "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                },
                {
                    "type": "rating",
                    "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                },
            ),
            (
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive", "description": "Text with a positive sentiment"},
                        {"value": "negative", "text": "Negative", "description": "Text with a negative sentiment"},
                        {"value": "neutral", "text": "Neutral", "description": "Text with a neutral sentiment"},
                    ],
                },
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive", "description": "Text with a positive sentiment"},
                        {"value": "negative", "text": "Negative", "description": "Text with a negative sentiment"},
                        {"value": "neutral", "text": "Neutral", "description": "Text with a neutral sentiment"},
                    ],
                    "visible_options": None,
                },
            ),
            (
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive"},
                        {"value": "negative", "text": "Negative"},
                        {"value": "neutral", "text": "Neutral"},
                    ],
                    "visible_options": 3,
                },
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive", "description": None},
                        {"value": "negative", "text": "Negative", "description": None},
                        {"value": "neutral", "text": "Neutral", "description": None},
                    ],
                    "visible_options": 3,
                },
            ),
            (
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": "Completion A is the best"},
                        {"value": "completion-b", "text": "Completion B", "description": "Completion B is the best"},
                        {"value": "completion-c", "text": "Completion C", "description": "Completion C is the best"},
                        {"value": "completion-d", "text": "Completion D", "description": "Completion D is the best"},
                    ],
                },
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": "Completion A is the best"},
                        {"value": "completion-b", "text": "Completion B", "description": "Completion B is the best"},
                        {"value": "completion-c", "text": "Completion C", "description": "Completion C is the best"},
                        {"value": "completion-d", "text": "Completion D", "description": "Completion D is the best"},
                    ],
                },
            ),
            (
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": None},
                        {"value": "completion-b", "text": "Completion b", "description": None},
                        {"value": "completion-c", "text": "Completion C", "description": None},
                        {"value": "completion-d", "text": "Completion D", "description": None},
                    ],
                },
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": None},
                        {"value": "completion-b", "text": "Completion b", "description": None},
                        {"value": "completion-c", "text": "Completion C", "description": None},
                        {"value": "completion-d", "text": "Completion D", "description": None},
                    ],
                },
            ),
            (
                {
                    "type": "span",
                    "field": "field-a",
                    "options": [
                        {"value": "label-a", "text": "Label A"},
                        {"value": "label-b", "text": "Label B"},
                        {"value": "label-c", "text": "Label C"},
                        {"value": "label-d", "text": "Label D"},
                    ],
                },
                {
                    "type": "span",
                    "field": "field-a",
                    "visible_options": None,
                    "options": [
                        {"value": "label-a", "text": "Label A", "description": None},
                        {"value": "label-b", "text": "Label B", "description": None},
                        {"value": "label-c", "text": "Label C", "description": None},
                        {"value": "label-d", "text": "Label D", "description": None},
                    ],
                    "allow_character_annotation": True,
                    "allow_overlapping": False,
                },
            ),
            (
                {
                    "type": "span",
                    "field": "field-a",
                    "visible_options": 3,
                    "options": [
                        {"value": "label-a", "text": "Label A"},
                        {"value": "label-b", "text": "Label B"},
                        {"value": "label-c", "text": "Label C"},
                        {"value": "label-d", "text": "Label D"},
                    ],
                },
                {
                    "type": "span",
                    "field": "field-a",
                    "visible_options": 3,
                    "options": [
                        {"value": "label-a", "text": "Label A", "description": None},
                        {"value": "label-b", "text": "Label B", "description": None},
                        {"value": "label-c", "text": "Label C", "description": None},
                        {"value": "label-d", "text": "Label D", "description": None},
                    ],
                    "allow_character_annotation": True,
                    "allow_overlapping": False,
                },
            ),
        ],
    )
    async def test_create_dataset_question(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        settings: dict,
        expected_settings: dict,
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(name="field-a", dataset=dataset)

        question_json = {
            "name": "name",
            "title": "title",
            "settings": settings,
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

        response_body = response.json()
        assert await db.get(Question, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "name": "name",
            "title": "title",
            "description": None,
            "required": False,
            "settings": expected_settings,
            "dataset_id": str(UUID(response_body["dataset_id"])),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    async def test_create_dataset_question_with_description(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "description": "description",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

        response_body = response.json()
        assert await db.get(Question, UUID(response_body["id"]))
        assert response_body["description"] == "description"

    async def test_create_dataset_question_without_authentication(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(f"/api/v1/datasets/{dataset.id}/questions", json=question_json)

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=question_json,
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

    async def test_create_dataset_question_as_admin_for_different_workspace(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])

        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=question_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json=question_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_invalid_max_length_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "a" * (QUESTION_CREATE_NAME_MAX_LENGTH + 1),
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_invalid_max_length_title(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "a" * (QUESTION_CREATE_TITLE_MAX_LENGTH + 1),
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_invalid_max_length_description(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "description": "a" * (QUESTION_CREATE_DESCRIPTION_MAX_LENGTH + 1),
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_existent_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        question = await QuestionFactory.create(name="name")

        response = await async_client.post(
            f"/api/v1/datasets/{question.dataset.id}/questions",
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {"type": "text"},
            },
        )

        assert response.status_code == 409
        assert response.json() == {
            "detail": f"Question with name `{question.name}` already exists for dataset with id `{question.dataset_id}`"
        }

        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

    async def test_create_dataset_question_with_published_dataset(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "questions cannot be created for a published dataset"}
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset_id = uuid4()

        await DatasetFactory.create()
        question_json = {
            "name": "text",
            "title": "Text",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset_id}/questions",
            headers=owner_auth_header,
            json=question_json,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Dataset with id `{dataset_id}` not found"}

        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "settings",
        [
            None,
            {},
            {"type": "wrong"},
            {"type": "text", "use_markdown": None},
            {"type": "text", "use_markdown": "wrong"},
            {
                "type": "rating",
                "options": [
                    {"value": "A wrong value"},
                    {"value": "B wrong value"},
                    {"value": "C wrong value"},
                    {"value": "D wrong value"},
                ],
            },
            {"type": "rating", "options": [{"value": value} for value in range(0, RATING_OPTIONS_MIN_ITEMS - 1)]},
            {"type": "rating", "options": [{"value": value} for value in range(0, RATING_OPTIONS_MAX_ITEMS + 1)]},
            {"type": "rating", "options": "invalid"},
            {"type": "rating", "options": [{"value": 1}, {"value": 1}]},
            {"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": 13}]},
            {"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": -13}]},
            {"type": "label_selection", "options": []},
            {"type": "label_selection", "options": [{"value": "just_one_label", "text": "Just one label"}]},
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": 0,
            },
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": -1,
            },
            {
                "type": "label_selection",
                "options": [{"value": "", "text": "a"}, {"value": "b", "text": "b"}],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "".join(["a" for _ in range(VALUE_TEXT_OPTION_VALUE_MAX_LENGTH + 1)]), "text": "a"},
                    {"value": "b", "text": "b"},
                ],
            },
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": ""}, {"value": "b", "text": "b"}],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "a", "text": "".join(["a" for _ in range(VALUE_TEXT_OPTION_TEXT_MAX_LENGTH + 1)])},
                    {"value": "b", "text": "b"},
                ],
            },
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a", "description": ""}, {"value": "b", "text": "b"}],
            },
            {
                "type": "label_selection",
                "options": [
                    {
                        "value": "a",
                        "text": "a",
                        "description": "".join(["a" for _ in range(VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH + 1)]),
                    },
                    {"value": "b", "text": "b"},
                ],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
                "visible_options": 2,
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
                "visible_options": 5,
            },
            {
                "type": "ranking",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {"value": value, "text": value, "description": value}
                    for value in range(0, RANKING_OPTIONS_MAX_ITEMS + 1)
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {
                        "value": "a",
                        "text": "a",
                        "description": "".join(["a" for _ in range(VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH + 1)]),
                    },
                    {"value": "b", "text": "b", "description": "b"},
                ],
            },
            {"type": "span", "options": []},
            {
                "type": "span",
                "options": [{"value": value, "text": value} for value in range(0, settings.span_options_max_items + 1)],
            },
        ],
    )
    async def test_create_dataset_question_with_invalid_settings(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        settings: dict,
    ):
        dataset = await DatasetFactory.create()
        question_json = {"name": "question", "title": "Question", "settings": settings}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0
