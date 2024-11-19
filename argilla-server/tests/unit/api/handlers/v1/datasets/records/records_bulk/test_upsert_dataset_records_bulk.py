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
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import User, Record
from argilla_server.jobs.queues import HIGH_QUEUE
from argilla_server.models import User, Record
from argilla_server.enums import DatasetDistributionStrategy, ResponseStatus, DatasetStatus, RecordStatus
from argilla_server.webhooks.v1.enums import RecordEvent
from argilla_server.webhooks.v1.records import build_record_event

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    TextFieldFactory,
    TextQuestionFactory,
    AnnotatorFactory,
    WebhookFactory,
    ResponseFactory,
)


@pytest.mark.asyncio
class TestUpsertDatasetRecordsBulk:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_upsert_dataset_records_with_empty_fields_creating_record(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="text-field", dataset=dataset)

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "text-field": "value",
                        },
                    },
                    {
                        "fields": {},
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Record at position 1 is not valid because fields cannot be empty"}

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_upsert_dataset_records_with_empty_fields_updating_record(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="text-field", dataset=dataset)

        record = await RecordFactory.create(fields={"text-field": "value"}, dataset=dataset)

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "text-field": "value",
                        },
                    },
                    {
                        "id": str(record.id),
                        "fields": {},
                    },
                ],
            },
        )

        assert response.status_code == 200

        assert record.fields == {"text-field": "value"}
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 2

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

    async def test_upsert_dataset_records_bulk_enqueue_webhook_record_created_events(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        webhook = await WebhookFactory.create(events=[RecordEvent.created, RecordEvent.updated])

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                        },
                    },
                    {
                        "fields": {
                            "prompt": "What is the best way to reduce stress?",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 200

        records = (await db.execute(select(Record).order_by(Record.inserted_at.asc()))).scalars().all()

        event_a = await build_record_event(db, RecordEvent.created, records[0])
        event_b = await build_record_event(db, RecordEvent.created, records[1])

        assert HIGH_QUEUE.count == 2

        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.created
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event_a.data)

        assert HIGH_QUEUE.jobs[1].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[1].args[1] == RecordEvent.created
        assert HIGH_QUEUE.jobs[1].args[3] == jsonable_encoder(event_b.data)

    async def test_upsert_dataset_records_bulk_enqueue_webhook_record_updated_events(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        records = await RecordFactory.create_batch(2, dataset=dataset)

        webhook = await WebhookFactory.create(events=[RecordEvent.created, RecordEvent.updated])

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(records[0].id),
                        "metadata": {
                            "metadata-key": "metadata-value",
                        },
                    },
                    {
                        "id": str(records[1].id),
                        "metadata": {
                            "metadata-key": "metadata-value",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 200

        event_a = await build_record_event(db, RecordEvent.updated, records[0])
        event_b = await build_record_event(db, RecordEvent.updated, records[1])

        assert HIGH_QUEUE.count == 2

        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.updated
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event_a.data)

        assert HIGH_QUEUE.jobs[1].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[1].args[1] == RecordEvent.updated
        assert HIGH_QUEUE.jobs[1].args[3] == jsonable_encoder(event_b.data)
