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
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from argilla_server.models import Response, User
from argilla_server.jobs.queues import HIGH_QUEUE
from argilla_server.webhooks.v1.enums import RecordEvent, ResponseEvent
from argilla_server.webhooks.v1.responses import build_response_event
from argilla_server.webhooks.v1.records import build_record_event
from argilla_server.enums import ResponseStatus, RecordStatus, DatasetDistributionStrategy

from tests.factories import DatasetFactory, RecordFactory, SpanQuestionFactory, TextQuestionFactory, WebhookFactory


@pytest.mark.asyncio
class TestCreateRecordResponse:
    def url(self, record_id: UUID) -> str:
        return f"/api/v1/records/{record_id}/responses"

    async def test_create_record_response_for_span_question(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 1},
                            {"label": "label-b", "start": 2, "end": 3},
                            {"label": "label-c", "start": 4, "end": 5},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        response_json = response.json()
        assert await db.get(Response, UUID(response_json["id"]))
        assert response_json == {
            "id": str(UUID(response_json["id"])),
            "values": {
                "span-question": {
                    "value": [
                        {"label": "label-a", "start": 0, "end": 1},
                        {"label": "label-b", "start": 2, "end": 3},
                        {"label": "label-c", "start": 4, "end": 5},
                    ],
                },
            },
            "status": ResponseStatus.submitted,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_json["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_json["updated_at"]).isoformat(),
        }

    async def test_create_record_response_for_span_question_with_additional_value_attributes(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 1, "ignored": "value"},
                            {"label": "label-b", "start": 2, "end": 3, "ignored": "value"},
                            {"label": "label-c", "start": 4, "end": 5},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        response_json = response.json()
        assert await db.get(Response, UUID(response_json["id"]))
        assert response_json == {
            "id": str(UUID(response_json["id"])),
            "values": {
                "span-question": {
                    "value": [
                        {"label": "label-a", "start": 0, "end": 1},
                        {"label": "label-b", "start": 2, "end": 3},
                        {"label": "label-c", "start": 4, "end": 5},
                    ],
                },
            },
            "status": ResponseStatus.submitted,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_json["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_json["updated_at"]).isoformat(),
        }

    async def test_create_record_response_for_span_question_with_empty_value(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        response_json = response.json()
        assert await db.get(Response, UUID(response_json["id"]))
        assert response_json == {
            "id": str(UUID(response_json["id"])),
            "values": {
                "span-question": {
                    "value": [],
                },
            },
            "status": ResponseStatus.submitted,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_json["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_json["updated_at"]).isoformat(),
        }

    async def test_create_record_response_for_span_question_with_record_not_providing_required_field(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"other-field": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 1},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "span question requires record to have field `field-a`"}

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_invalid_value(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 1},
                            {"invalid": "value"},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_start_greater_than_expected(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 5, "end": 6}],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "span question response value `start` must have a value lower than record field `field-a` length that is `5`"
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_end_greater_than_expected(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 4, "end": 6}],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "span question response value `end` must have a value lower or equal than record field `field-a` length that is `5`"
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_invalid_start(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": -1, "end": 1},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_invalid_end(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 0},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_equal_start_and_end(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 1, "end": 1},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_end_smaller_than_start(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 3, "end": 2},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_non_existent_label(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-non-existent", "start": 1, "end": 2},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "undefined label 'label-non-existent' for span question.\n"
            "Valid labels are: ['label-a', 'label-b', 'label-c']"
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_for_span_question_with_overlapped_values(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello, this is a text field"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 3},
                            {"label": "label-a", "start": 6, "end": 8},
                            {"label": "label-b", "start": 2, "end": 5},
                        ],
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "overlapping values found between spans at index idx=0 and idx=2"}

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_updates_record_status_to_completed(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            }
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "text-question": {
                        "value": "text question response",
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 201
        assert record.status == RecordStatus.completed

    async def test_create_record_response_does_not_updates_record_status_to_completed(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            }
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "text-question": {
                        "value": "text question response",
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 201
        assert record.status == RecordStatus.pending

    async def test_create_record_response_enqueue_webhook_response_created_event(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            }
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        webhook = await WebhookFactory.create(events=[ResponseEvent.created])

        resp = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "text-question": {
                        "value": "text question response",
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert resp.status_code == 201

        response = (await db.execute(select(Response))).scalar_one()
        event = await build_response_event(db, ResponseEvent.created, response)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == ResponseEvent.created
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)

    async def test_create_record_response_enqueue_webhook_record_updated_event(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            }
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        webhook = await WebhookFactory.create(events=[RecordEvent.updated])

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "text-question": {
                        "value": "text question response",
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 201

        event = await build_record_event(db, RecordEvent.updated, record)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.updated
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)

    async def test_create_record_response_enqueue_webhook_record_completed_event(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            }
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        webhook = await WebhookFactory.create(events=[RecordEvent.completed])

        response = await async_client.post(
            self.url(record.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "text-question": {
                        "value": "text question response",
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert response.status_code == 201

        event = await build_record_event(db, RecordEvent.completed, record)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.completed
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)
