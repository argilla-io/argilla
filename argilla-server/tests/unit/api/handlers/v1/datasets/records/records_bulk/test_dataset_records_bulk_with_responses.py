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
from argilla_server.models import Dataset, Response
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    LabelSelectionQuestionFactory,
    OwnerFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    TextQuestionFactory,
)


@pytest.mark.asyncio
class TestDatasetRecordsBulkWithResponses:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_dataset(self, **kwargs) -> Dataset:
        dataset = await DatasetFactory.create(status=DatasetStatus.ready, **kwargs)

        await self._configure_dataset_fields(dataset)
        await self._configure_dataset_questions(dataset)

        return dataset

    async def test_create_record_with_responses_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        user = await OwnerFactory.create()

        http_response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "responses": [
                            {
                                "user_id": str(user.id),
                                "values": {"label": {"value": "label-a"}},
                                "status": "submitted",
                            }
                        ],
                    },
                ]
            },
        )

        assert http_response.status_code == 201, http_response.json()
        assert (await db.execute(select(func.count(Response.id)))).scalar_one() == 1
        response = (await db.execute(select(Response))).scalar_one()

        response_json = http_response.json()
        for record in response_json["items"]:
            assert record["responses"] == [
                {
                    "id": str(response.id),
                    "user_id": str(user.id),
                    "record_id": record["id"],
                    "values": {"label": {"value": "label-a"}},
                    "status": "submitted",
                    "inserted_at": response.inserted_at.isoformat(),
                    "updated_at": response.updated_at.isoformat(),
                },
            ]

    async def test_update_records_with_new_responses_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        user = await OwnerFactory.create()
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})

        http_response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "responses": [
                            {
                                "user_id": str(user.id),
                                "values": {},
                                "status": "discarded",
                            }
                        ],
                    },
                ]
            },
        )

        assert http_response.status_code == 200, http_response.json()
        assert (await db.execute(select(func.count(Response.id)))).scalar_one() == 1
        response = (await db.execute(select(Response))).scalar_one()

        response_json = http_response.json()
        records = response_json["items"]

        for record in records:
            assert record["responses"] == [
                {
                    "id": str(response.id),
                    "user_id": str(user.id),
                    "record_id": record["id"],
                    "values": {},
                    "status": "discarded",
                    "inserted_at": response.inserted_at.isoformat(),
                    "updated_at": response.updated_at.isoformat(),
                },
            ]

    async def test_create_records_with_responses_in_bulk_upsert(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        user = await OwnerFactory.create()
        http_response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "responses": [
                            {
                                "user_id": str(user.id),
                                "values": {"label": {"value": "label-a"}},
                                "status": "submitted",
                            }
                        ],
                    },
                ]
            },
        )

        assert http_response.status_code == 200, http_response.json()
        assert (await db.execute(select(func.count(Response.id)))).scalar_one() == 1
        response = (await db.execute(select(Response))).scalar_one()

        response_json = http_response.json()
        records = response_json["items"]
        for record in records:
            assert record["responses"] == [
                {
                    "id": str(response.id),
                    "user_id": str(user.id),
                    "record_id": record["id"],
                    "values": {"label": {"value": "label-a"}},
                    "status": "submitted",
                    "inserted_at": response.inserted_at.isoformat(),
                    "updated_at": response.updated_at.isoformat(),
                },
            ]

    async def test_update_record_responses_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        user = await OwnerFactory.create()
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        response = await ResponseFactory.create(
            record=record, user=user, values={"label": {"value": "label-a"}}, status="submitted"
        )

        http_response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "responses": [
                            {
                                "user_id": str(user.id),
                                "values": {},
                                "status": "draft",
                            }
                        ],
                    },
                ]
            },
        )

        assert http_response.status_code == 200, http_response.json()
        assert (await db.execute(select(func.count(Response.id)))).scalar_one() == 1

        records = http_response.json()["items"]
        for record in records:
            assert record["responses"] == [
                {
                    "id": str(response.id),
                    "user_id": str(user.id),
                    "record_id": record["id"],
                    "values": {},
                    "status": "draft",
                    "inserted_at": response.inserted_at.isoformat(),
                    "updated_at": response.updated_at.isoformat(),
                },
            ]

        response = (await db.execute(select(Response))).scalar_one()
        assert response.status == "draft"

    async def test_update_record_with_responses_with_new_responses_in_bulk(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        user = await OwnerFactory.create()
        other_user = await OwnerFactory.create()
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        await ResponseFactory.create(
            record=record, user=user, values={"label": {"value": "label-a"}}, status="submitted"
        )

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "responses": [
                            {
                                "user_id": str(other_user.id),
                                "status": "discarded",
                            }
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()

        records = response.json()["items"]
        for record in records:
            assert record["responses"] == [
                {
                    "id": record["responses"][0]["id"],
                    "user_id": str(user.id),
                    "record_id": record["id"],
                    "values": {"label": {"value": "label-a"}},
                    "status": "submitted",
                    "inserted_at": record["responses"][0]["inserted_at"],
                    "updated_at": record["responses"][0]["updated_at"],
                },
                {
                    "id": record["responses"][1]["id"],
                    "user_id": str(other_user.id),
                    "record_id": record["id"],
                    "values": None,
                    "status": "discarded",
                    "inserted_at": record["responses"][1]["inserted_at"],
                    "updated_at": record["responses"][1]["updated_at"],
                },
            ]

    async def test_create_record_with_with_wrong_response_question(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        user = await OwnerFactory.create()
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
                        "responses": [
                            {
                                "user_id": str(user.id),
                                "values": {"other-question": {"value": "wrong value"}},
                                "status": "draft",
                            },
                        ],
                    },
                ],
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": "Record at position 0 does not have valid responses because "
            "found response value for non configured question with name='other-question'"
        }

    async def test_update_record_with_wrong_responses_values(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await self.test_dataset()
        user = await OwnerFactory.create()
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
                        "responses": [
                            {
                                "user_id": str(user.id),
                                "values": {"label": {"value": "wrong-label"}},
                                "status": "draft",
                            }
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": "Record at position 0 does not have valid responses because 'wrong-label' "
            "is not a valid label for label selection question.\n"
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

        await dataset.awaitable_attrs.questions
