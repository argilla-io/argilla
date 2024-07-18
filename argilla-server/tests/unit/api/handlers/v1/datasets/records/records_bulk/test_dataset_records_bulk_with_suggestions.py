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
from argilla_server.enums import DatasetStatus, QuestionType
from argilla_server.models import Dataset, Suggestion
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    LabelSelectionQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    SuggestionFactory,
    TextFieldFactory,
    TextQuestionFactory,
)


@pytest.mark.asyncio
class TestDatasetRecordsBulkWithSuggestions:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_dataset(self, **kwargs) -> Dataset:
        dataset = await DatasetFactory.create(status=DatasetStatus.ready, **kwargs)

        await self._configure_dataset_fields(dataset)
        await self._configure_dataset_questions(dataset)

        return dataset

    async def test_create_record_with_suggestions_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        label_question = dataset.question_by_name("label")

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "suggestions": [
                            {"question_id": str(label_question.id), "value": "label-a"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 201, response.json()
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar_one() == 1
        suggestion = (await db.execute(select(Suggestion))).scalar_one()

        response_json = response.json()
        for record in response_json["items"]:
            assert record["suggestions"] == [
                {
                    "id": str(suggestion.id),
                    "question_id": str(label_question.id),
                    "value": "label-a",
                    "score": suggestion.score,
                    "type": suggestion.type,
                    "agent": suggestion.agent,
                    "inserted_at": suggestion.inserted_at.isoformat(),
                    "updated_at": suggestion.updated_at.isoformat(),
                },
            ]

    async def test_update_records_with_new_suggestions_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        question_id = str(dataset.question_by_name("label").id)

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "suggestions": [
                            {"question_id": question_id, "value": "label-a"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar_one() == 1
        suggestion = (await db.execute(select(Suggestion))).scalar_one()

        response_json = response.json()
        records = response_json["items"]
        for record in records:
            assert record["suggestions"] == [
                {
                    "id": str(suggestion.id),
                    "question_id": question_id,
                    "value": "label-a",
                    "score": suggestion.score,
                    "type": suggestion.type,
                    "agent": suggestion.agent,
                    "inserted_at": suggestion.inserted_at.isoformat(),
                    "updated_at": suggestion.updated_at.isoformat(),
                },
            ]

    async def test_create_records_with_suggestions_in_bulk_upsert(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        question_id = str(dataset.question_by_name("label").id)

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "suggestions": [
                            {"question_id": question_id, "value": "label-a"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar_one() == 1
        suggestion = (await db.execute(select(Suggestion))).scalar_one()

        response_json = response.json()
        for record in response_json["items"]:
            assert record["suggestions"] == [
                {
                    "id": str(suggestion.id),
                    "question_id": question_id,
                    "value": "label-a",
                    "score": suggestion.score,
                    "type": suggestion.type,
                    "agent": suggestion.agent,
                    "inserted_at": suggestion.inserted_at.isoformat(),
                    "updated_at": suggestion.updated_at.isoformat(),
                },
            ]

    async def test_update_record_suggestions_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        question = dataset.question_by_name("label")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        await SuggestionFactory.create(record=record, question=question, value="label-a")

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "suggestions": [
                            {"question_id": str(question.id), "value": "label-b"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar_one() == 1
        suggestion = (await db.execute(select(Suggestion))).scalar_one()

        records = response.json()["items"]
        assert len(records) == 1
        for record in records:
            assert record["suggestions"] == [
                {
                    "id": str(suggestion.id),
                    "question_id": str(question.id),
                    "value": "label-b",
                    "score": suggestion.score,
                    "type": suggestion.type,
                    "agent": suggestion.agent,
                    "inserted_at": suggestion.inserted_at.isoformat(),
                    "updated_at": suggestion.updated_at.isoformat(),
                },
            ]
        assert suggestion.value == "label-b"

    async def test_update_record_with_suggestions_with_new_suggestions_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        question = dataset.question_by_name("label")
        other_question = dataset.question_by_name("rating")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        suggestion = await SuggestionFactory.create(record=record, question=question, value="label-a")

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "suggestions": [
                            {"question_id": str(other_question.id), "value": 5, "agent": "test-agent", "score": 0.5},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar_one() == 2
        other_suggestion = (
            await db.execute(select(Suggestion).filter(Suggestion.question_id == other_question.id))
        ).scalar_one()

        records = response.json()["items"]
        assert len(records) == 1
        for record in records:
            assert record["suggestions"] == [
                {
                    "id": str(suggestion.id),
                    "question_id": str(question.id),
                    "value": suggestion.value,
                    "score": suggestion.score,
                    "type": suggestion.type,
                    "agent": suggestion.agent,
                    "inserted_at": suggestion.inserted_at.isoformat(),
                    "updated_at": suggestion.updated_at.isoformat(),
                },
                {
                    "id": str(other_suggestion.id),
                    "question_id": str(other_question.id),
                    "value": 5,
                    "score": other_suggestion.score,
                    "type": other_suggestion.type,
                    "agent": other_suggestion.agent,
                    "inserted_at": other_suggestion.inserted_at.isoformat(),
                    "updated_at": other_suggestion.updated_at.isoformat(),
                },
            ]

    async def test_create_record_with_wrong_suggestion_question_id_in_bulk(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        other_question = await TextQuestionFactory.create(name="other-question")

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "suggestions": [
                            {"question_id": str(other_question.id), "value": "label-c"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": "Record at position 0 does not have valid suggestions because "
            f"question with question_id={other_question.id} does not exist"
        }

    async def test_create_record_with_wrong_suggestion_value_in_bulk(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        question_id = str(dataset.question_by_name("label").id)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "suggestions": [
                            {"question_id": question_id, "value": "wrong-label"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": "Record at position 0 does not have valid suggestions because suggestion for question name=label "
            "is not valid: 'wrong-label' is not a valid label for label selection question.\n"
            "Valid labels are: ['label-a', 'label-b']"
        }

    async def test_update_record_with_wrong_suggestion_question_id_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        question = dataset.question_by_name("label")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        suggestion = await SuggestionFactory.create(record=record, question=question, value="label-a")
        other_question = await TextQuestionFactory.create(name="other-question")

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "suggestions": [
                            {"question_id": str(other_question.id), "value": "label-c"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": f"Record at position 0 does not have valid suggestions because "
            f"question with question_id={other_question.id} does not exist"
        }

    async def test_update_record_with_wrong_suggestion_value_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        question = dataset.question_by_name("label")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        suggestion = await SuggestionFactory.create(record=record, question=question, value="label-a")

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "suggestions": [
                            {"question_id": str(question.id), "value": "wrong-label"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": "Record at position 0 does not have valid suggestions because suggestion for question name=label "
            "is not valid: 'wrong-label' is not a valid label for label selection question.\n"
            "Valid labels are: ['label-a', 'label-b']"
        }

    async def _configure_dataset_fields(self, dataset: Dataset):
        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextFieldFactory.create(name="response", dataset=dataset)

        await dataset.awaitable_attrs.fields

    async def _configure_dataset_questions(self, dataset: Dataset):
        await LabelSelectionQuestionFactory.create(
            dataset=dataset,
            name="label",
            settings={
                "type": QuestionType.label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                ],
            },
        )

        await RatingQuestionFactory.create(dataset=dataset, name="rating")

        await dataset.awaitable_attrs.questions
