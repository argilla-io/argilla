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

import pytest

from uuid import UUID
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import User, Record
from argilla_server.enums import DatasetDistributionStrategy, RecordStatus, ResponseStatus, DatasetStatus

from tests.factories import AnnotatorFactory, DatasetFactory, TextFieldFactory, TextQuestionFactory


@pytest.mark.asyncio
class TestCreateDatasetRecordsBulk:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_create_dataset_records_bulk_updates_records_status(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            status=DatasetStatus.ready,
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            },
        )

        user = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextFieldFactory.create(name="response", dataset=dataset)

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

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
                                "user_id": str(owner.id),
                                "status": ResponseStatus.submitted,
                                "values": {
                                    "text-question": {
                                        "value": "text question response",
                                    },
                                },
                            },
                            {
                                "user_id": str(user.id),
                                "status": ResponseStatus.submitted,
                                "values": {
                                    "text-question": {
                                        "value": "text question response",
                                    },
                                },
                            },
                        ],
                    },
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "responses": [
                            {
                                "user_id": str(owner.id),
                                "status": ResponseStatus.submitted,
                                "values": {
                                    "text-question": {
                                        "value": "text question response",
                                    },
                                },
                            },
                        ],
                    },
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "responses": [
                            {
                                "user_id": str(owner.id),
                                "status": ResponseStatus.draft,
                                "values": {
                                    "text-question": {
                                        "value": "text question response",
                                    },
                                },
                            },
                            {
                                "user_id": str(user.id),
                                "status": ResponseStatus.draft,
                                "values": {
                                    "text-question": {
                                        "value": "text question response",
                                    },
                                },
                            },
                        ],
                    },
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 201

        response_items = response.json()["items"]
        assert response_items[0]["status"] == RecordStatus.completed
        assert response_items[1]["status"] == RecordStatus.pending
        assert response_items[2]["status"] == RecordStatus.pending
        assert response_items[3]["status"] == RecordStatus.pending

        assert (await Record.get(db, UUID(response_items[0]["id"]))).status == RecordStatus.completed
        assert (await Record.get(db, UUID(response_items[1]["id"]))).status == RecordStatus.pending
        assert (await Record.get(db, UUID(response_items[2]["id"]))).status == RecordStatus.pending
        assert (await Record.get(db, UUID(response_items[3]["id"]))).status == RecordStatus.pending
