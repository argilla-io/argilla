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
from uuid import UUID

import pytest
from argilla_server.enums import DatasetStatus, OptionsOrder, QuestionType
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    LabelSelectionQuestionFactory,
    QuestionFactory,
    SpanQuestionFactory,
    TextQuestionFactory,
)


@pytest.mark.asyncio
class TestUpdateQuestion:
    def url(self, question_id: UUID) -> str:
        return f"/api/v1/questions/{question_id}"

    async def test_update_question_name_attribute_with_draft_dataset(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.draft)
        text_question = await TextQuestionFactory.create(dataset=dataset)

        response = await async_client.patch(
            self.url(text_question.id),
            headers=owner_auth_header,
            json={"name": "updated-name"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "updated-name"

        assert text_question.name == "updated-name"

    async def test_update_question_name_attribute_with_published_dataset(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        text_question = await TextQuestionFactory.create(name="text-question", dataset=dataset)

        response = await async_client.patch(
            self.url(text_question.id),
            headers=owner_auth_header,
            json={"name": "updated-name"},
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Question name cannot be changed for questions belonging to a published dataset"
        }

        assert text_question.name == "text-question"

    async def test_update_question_required_attribute_with_draft_dataset(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.draft)
        text_question = await TextQuestionFactory.create(dataset=dataset)

        response = await async_client.patch(
            self.url(text_question.id),
            headers=owner_auth_header,
            json={"required": True},
        )

        assert response.status_code == 200
        assert response.json()["required"] is True

        assert text_question.required is True

    async def test_update_question_required_attribute_with_published_dataset(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        text_question = await TextQuestionFactory.create(required=True, dataset=dataset)

        response = await async_client.patch(
            self.url(text_question.id),
            headers=owner_auth_header,
            json={"required": False},
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Question required flag cannot be changed for questions belonging to a published dataset"
        }

        assert text_question.required is True

    async def test_update_question_with_different_type(self, async_client: AsyncClient, owner_auth_header: dict):
        question = await TextQuestionFactory.create()

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {
                    "type": QuestionType.label_selection,
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "question type cannot be changed. expected 'text' but got 'label_selection'"
        }

    async def test_update_question_with_different_number_of_options(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await LabelSelectionQuestionFactory.create()

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {
                    "type": QuestionType.label_selection,
                    "options": [
                        {"value": "label-a", "text": "Label A"},
                        {"value": "label-b", "text": "Label B"},
                        {"value": "label-c", "text": "Label C"},
                        {"value": "label-d", "text": "Label D"},
                    ],
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "the number of options cannot be modified. expected 3 but got 4"}

    async def test_update_question_with_different_options(self, async_client: AsyncClient, owner_auth_header: dict):
        question = await LabelSelectionQuestionFactory.create()

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {
                    "type": QuestionType.label_selection,
                    "options": [
                        {"value": "label-a", "text": "Label A"},
                        {"value": "label-b", "text": "Label B"},
                        {"value": "label-c", "text": "Label C"},
                    ],
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "the option values cannot be modified. found unexpected option values: ['label-a', 'label-b', 'label-c']"
        }

    async def test_update_multi_label_selection_question_with_options_order(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await QuestionFactory.create(
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                ],
                "options_order": OptionsOrder.natural,
            }
        )

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {
                    "type": QuestionType.multi_label_selection,
                    "options_order": OptionsOrder.suggestion,
                },
            },
        )

        assert response.status_code == 200
        assert response.json()["settings"]["options_order"] == OptionsOrder.suggestion
        assert question.settings["options_order"] == OptionsOrder.suggestion

    async def test_update_multi_label_selection_question_without_options_order(
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
            }
        )

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={"type": QuestionType.multi_label_selection},
        )

        assert response.status_code == 200
        assert response.json()["settings"]["options_order"] == OptionsOrder.suggestion
        assert question.settings["options_order"] == OptionsOrder.suggestion

    async def test_update_multi_label_selection_question_with_options_order_as_none(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await QuestionFactory.create(
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                ],
                "options_order": OptionsOrder.natural,
            }
        )

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {
                    "type": QuestionType.multi_label_selection,
                    "options_order": None,
                },
            },
        )

        assert response.status_code == 422
        assert question.settings["options_order"] == OptionsOrder.natural

    async def test_update_question_with_more_visible_options_than_allowed(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await LabelSelectionQuestionFactory.create()

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {
                    "type": QuestionType.label_selection,
                    "visible_options": 4,
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "the value for 'visible_options' must be less or equal to the number of items in 'options' (3)"
        }

    async def test_update_span_question_enabling_allow_overlapping(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await SpanQuestionFactory.create(
            settings={
                "type": QuestionType.span.value,
                "field": "field-a",
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
                "allow_overlapping": False,
            }
        )

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {"type": QuestionType.span, "allow_overlapping": True},
            },
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            "id": str(question.id),
            "name": question.name,
            "description": question.description,
            "title": question.title,
            "dataset_id": str(question.dataset_id),
            "required": False,
            "settings": {
                "type": QuestionType.span.value,
                "field": "field-a",
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
                "allow_overlapping": True,
                "allow_character_annotation": True,
                "visible_options": None,
            },
            "inserted_at": datetime.fromisoformat(response_json["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_json["updated_at"]).isoformat(),
        }

    async def test_update_span_question_disabling_allow_overlapping(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        question = await SpanQuestionFactory.create(
            settings={
                "type": QuestionType.span.value,
                "field": "field-a",
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
                "allow_overlapping": True,
            }
        )

        response = await async_client.patch(
            self.url(question.id),
            headers=owner_auth_header,
            json={
                "settings": {"type": QuestionType.span, "allow_overlapping": False},
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "'allow_overlapping' can't be disabled because responses may become inconsistent"
        }
