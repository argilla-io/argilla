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

from argilla_server.models import User
from argilla_server.enums import DatasetDistributionStrategy, ResponseStatus, DatasetStatus, RecordStatus

from tests.factories import DatasetFactory, RecordFactory, TextQuestionFactory, ResponseFactory, AnnotatorFactory


@pytest.mark.asyncio
class TestUpsertDatasetRecordsBulk:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_upsert_dataset_records_bulk_updates_records_status(
        self, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            status=DatasetStatus.ready,
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            },
        )

        user = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record_a = await RecordFactory.create(dataset=dataset)
        assert record_a.status == RecordStatus.pending

        await ResponseFactory.create(
            user=owner,
            record=record_a,
            status=ResponseStatus.submitted,
            values={
                "text-question": {
                    "value": "text question response",
                },
            },
        )

        record_b = await RecordFactory.create(dataset=dataset)
        assert record_b.status == RecordStatus.pending

        record_c = await RecordFactory.create(dataset=dataset)
        assert record_c.status == RecordStatus.pending

        record_d = await RecordFactory.create(dataset=dataset)
        assert record_d.status == RecordStatus.pending

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record_a.id),
                        "responses": [
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
                        "id": str(record_b.id),
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
                        "id": str(record_c.id),
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
                        "id": str(record_d.id),
                        "responses": [],
                    },
                ],
            },
        )

        assert response.status_code == 200

        respose_items = response.json()["items"]
        assert respose_items[0]["status"] == RecordStatus.completed
        assert respose_items[1]["status"] == RecordStatus.pending
        assert respose_items[2]["status"] == RecordStatus.pending
        assert respose_items[3]["status"] == RecordStatus.pending

        assert record_a.status == RecordStatus.completed
        assert record_b.status == RecordStatus.pending
        assert record_c.status == RecordStatus.pending
        assert record_d.status == RecordStatus.pending
