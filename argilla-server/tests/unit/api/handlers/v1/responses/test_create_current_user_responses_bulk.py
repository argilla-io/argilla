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

import os
import pytest

from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import call
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import DatasetDistributionStrategy, ResponseStatus, RecordStatus
from argilla_server.jobs.queues import HIGH_QUEUE
from argilla_server.models import Response, User
from argilla_server.search_engine import SearchEngine
from argilla_server.use_cases.responses.upsert_responses_in_bulk import UpsertResponsesInBulkUseCase
from argilla_server.webhooks.v1.enums import RecordEvent, ResponseEvent
from argilla_server.webhooks.v1.responses import build_response_event
from argilla_server.webhooks.v1.records import build_record_event
from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    WebhookFactory,
    WorkspaceUserFactory,
    TextQuestionFactory,
)


@pytest.mark.asyncio
class TestCreateCurrentUserResponsesBulk:
    def url(self) -> str:
        return "/api/v1/me/responses/bulk"

    def bulk_max_items(self) -> int:
        return 100

    async def test_multiple_responses(
        self, async_client: AsyncClient, db: AsyncSession, mock_search_engine: SearchEngine
    ):
        dataset = await DatasetFactory.create()
        await RatingQuestionFactory.create(name="prompt-quality", required=True, dataset=dataset)

        annotator = await AnnotatorFactory.create()
        await WorkspaceUserFactory.create(user_id=annotator.id, workspace_id=dataset.workspace.id)

        records = await RecordFactory.create_batch(3, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        other_record = await RecordFactory.create(dataset=other_dataset)

        response_to_create_json = {
            "values": {"prompt-quality": {"value": 5}},
            "status": ResponseStatus.submitted,
            "record_id": str(records[0].id),
        }

        response_to_update = await ResponseFactory.create(
            status=ResponseStatus.draft,
            values={"prompt-quality": {"value": 1}},
            record=records[1],
            user=annotator,
        )

        response_to_update_json = {
            "values": {"prompt-quality": {"value": 10}},
            "status": ResponseStatus.submitted,
            "record_id": str(response_to_update.record_id),
        }

        invalid_response_json = {
            "values": {"non-existent-question": {"value": 10}},
            "status": ResponseStatus.submitted,
            "record_id": str(records[2].id),
        }

        unauthorized_response_json = {
            "status": ResponseStatus.draft,
            "record_id": str(other_record.id),
        }

        resp = await async_client.post(
            self.url(),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={
                "items": [
                    response_to_create_json,
                    response_to_update_json,
                    invalid_response_json,
                    unauthorized_response_json,
                ],
            },
        )

        assert resp.status_code == 200

        resp_json = resp.json()
        response_to_create_id = UUID(resp_json["items"][0]["item"]["id"])
        assert resp_json == {
            "items": [
                {
                    "item": {
                        "id": str(response_to_create_id),
                        "values": {"prompt-quality": {"value": 5}},
                        "status": ResponseStatus.submitted,
                        "record_id": str(records[0].id),
                        "user_id": str(annotator.id),
                        "inserted_at": datetime.fromisoformat(resp_json["items"][0]["item"]["inserted_at"]).isoformat(),
                        "updated_at": datetime.fromisoformat(resp_json["items"][0]["item"]["updated_at"]).isoformat(),
                    },
                    "error": None,
                },
                {
                    "item": {
                        "id": str(response_to_update.id),
                        "values": {"prompt-quality": {"value": 10}},
                        "status": ResponseStatus.submitted,
                        "record_id": str(records[1].id),
                        "user_id": str(annotator.id),
                        "inserted_at": datetime.fromisoformat(resp_json["items"][1]["item"]["inserted_at"]).isoformat(),
                        "updated_at": datetime.fromisoformat(resp_json["items"][1]["item"]["updated_at"]).isoformat(),
                    },
                    "error": None,
                },
                {
                    "item": None,
                    "error": {
                        "detail": "missing response value for required question with name='prompt-quality'",
                    },
                },
                {
                    "item": None,
                    "error": {
                        "detail": "argilla.api.errors::ForbiddenOperationError(detail=Operation not allowed)",
                    },
                },
            ],
        }

        assert records[0].status == RecordStatus.completed
        assert records[1].status == RecordStatus.completed
        assert records[2].status == RecordStatus.pending

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 2

        response_to_create = (await db.execute(select(Response).filter_by(id=response_to_create_id))).scalar_one()
        await db.refresh(response_to_update)
        expected_calls = [
            call(response_to_create),
            call(response_to_update),
        ]
        mock_search_engine.update_record_response.assert_has_calls(expected_calls)

    async def test_response_to_create(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create()
        await RatingQuestionFactory.create(name="prompt-quality", required=True, dataset=dataset)

        record = await RecordFactory.create(dataset=dataset)

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "values": {"prompt-quality": {"value": 10}},
                        "status": ResponseStatus.submitted,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200

        resp_json = resp.json()
        response_id = UUID(resp_json["items"][0]["item"]["id"])
        assert resp_json == {
            "items": [
                {
                    "item": {
                        "id": str(response_id),
                        "values": {"prompt-quality": {"value": 10}},
                        "status": ResponseStatus.submitted.value,
                        "record_id": str(record.id),
                        "user_id": str(owner.id),
                        "inserted_at": datetime.fromisoformat(resp_json["items"][0]["item"]["inserted_at"]).isoformat(),
                        "updated_at": datetime.fromisoformat(resp_json["items"][0]["item"]["updated_at"]).isoformat(),
                    },
                    "error": None,
                },
            ],
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        response = (await db.execute(select(Response).filter_by(id=response_id))).scalar_one()
        mock_search_engine.update_record_response.assert_called_once_with(response)

    async def test_response_to_create_with_non_existent_record(
        self, async_client: AsyncClient, db: AsyncSession, mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        non_existent_record_id = uuid4()

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "status": ResponseStatus.draft,
                        "record_id": str(non_existent_record_id),
                    },
                ],
            },
        )

        assert resp.status_code == 200
        assert resp.json() == {
            "items": [
                {
                    "item": None,
                    "error": {
                        "detail": f"Record with id `{non_existent_record_id}` not found",
                    },
                },
            ],
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert not mock_search_engine.update_record_response.called

    async def test_response_to_update(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create()
        await RatingQuestionFactory.create(name="prompt-quality", required=True, dataset=dataset)

        record = await RecordFactory.create(dataset=dataset)
        response = await ResponseFactory.create(
            status=ResponseStatus.draft,
            values={"prompt-quality": {"value": 1}},
            record=record,
            user=owner,
        )

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "values": {"prompt-quality": {"value": 10}},
                        "status": ResponseStatus.submitted,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200

        resp_json = resp.json()
        assert resp_json == {
            "items": [
                {
                    "item": {
                        "id": str(response.id),
                        "values": {"prompt-quality": {"value": 10}},
                        "status": ResponseStatus.submitted.value,
                        "record_id": str(record.id),
                        "user_id": str(owner.id),
                        "inserted_at": datetime.fromisoformat(resp_json["items"][0]["item"]["inserted_at"]).isoformat(),
                        "updated_at": datetime.fromisoformat(resp_json["items"][0]["item"]["updated_at"]).isoformat(),
                    },
                    "error": None,
                },
            ],
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        await db.refresh(response)
        mock_search_engine.update_record_response.assert_called_once_with(response)

    async def test_invalid_response(
        self, async_client: AsyncClient, db: AsyncSession, mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "values": {"prompt-quality": {"value": 10}},
                        "status": ResponseStatus.submitted,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200
        assert resp.json() == {
            "items": [
                {
                    "item": None,
                    "error": {
                        "detail": "found response value for non configured question with name='prompt-quality'",
                    },
                },
            ],
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert not mock_search_engine.update_record_response.called

    async def test_unauthorized_response(
        self, async_client: AsyncClient, mock_search_engine: SearchEngine, db: AsyncSession
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)
        annotator = await AnnotatorFactory.create()

        resp = await async_client.post(
            self.url(),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={
                "items": [
                    {
                        "status": ResponseStatus.draft,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200
        assert resp.json() == {
            "items": [
                {
                    "item": None,
                    "error": {
                        "detail": "argilla.api.errors::ForbiddenOperationError(detail=Operation not allowed)",
                    },
                },
            ],
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert not mock_search_engine.update_record_response.called

    async def test_no_responses(self, async_client: AsyncClient, owner_auth_header: dict):
        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={"items": []},
        )

        assert resp.status_code == 422

    async def test_too_many_responses(self, async_client: AsyncClient, owner_auth_header: dict):
        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={"items": [{}] * (self.bulk_max_items() + 1)},
        )

        assert resp.status_code == 422

    @pytest.mark.skipif(reason="Profiling is not active", condition=not bool(os.getenv("TEST_PROFILING", None)))
    async def test_create_responses_in_bulk_profiling(self, db: "AsyncSession", elasticsearch_config: dict):
        from argilla_server.api.schemas.v1.responses import DraftResponseUpsert
        from argilla_server.search_engine import ElasticSearchEngine
        from pyinstrument import Profiler

        from tests.factories import OwnerFactory, TextFieldFactory

        async def refresh_dataset(dataset):
            await dataset.awaitable_attrs.fields
            await dataset.awaitable_attrs.questions
            await dataset.awaitable_attrs.metadata_properties
            await dataset.awaitable_attrs.vectors_settings

        async def refresh_records(records):
            for record in records:
                await record.awaitable_attrs.suggestions
                await record.awaitable_attrs.responses
                await record.awaitable_attrs.vectors

        dataset = await DatasetFactory.create()
        user = await OwnerFactory.create()

        await RatingQuestionFactory.create(name="prompt-quality", required=True, dataset=dataset)
        await TextFieldFactory.create(name="text", required=True, dataset=dataset)
        await TextFieldFactory.create(name="sentiment", required=True, dataset=dataset)

        records = await RecordFactory.create_batch(dataset=dataset, size=500)

        engine = ElasticSearchEngine(config=elasticsearch_config, number_of_replicas=0, number_of_shards=1)

        await refresh_dataset(dataset)
        await refresh_records(records)

        await engine.create_index(dataset)
        await engine.index_records(dataset, records)

        profiler = Profiler()

        responses = [
            DraftResponseUpsert.model_validate(
                {
                    "values": {"prompt-quality": {"value": 10}},
                    "record_id": record.id,
                    "status": "draft",
                }
            )
            for record in records
        ]
        use_case = UpsertResponsesInBulkUseCase(db, engine)
        with profiler:
            bulk_items = await use_case.execute(responses, user)
            await use_case.execute([bulk_item.item for bulk_item in bulk_items], user)

        profiler.open_in_browser()

    async def test_create_current_user_responses_bulk_enqueue_webhook_response_created_event(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            },
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        webhook = await WebhookFactory.create(events=[ResponseEvent.created, ResponseEvent.updated])

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "values": {
                            "text-question": {
                                "value": "Created value",
                            },
                        },
                        "status": ResponseStatus.submitted,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200

        response = (await db.execute(select(Response))).scalar_one()
        event = await build_response_event(db, ResponseEvent.created, response)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == ResponseEvent.created
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)

    async def test_create_current_user_responses_bulk_enqueue_webhook_response_updated_event(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            },
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response = await ResponseFactory.create(
            values={"text-question": {"value": "Created value"}},
            status=ResponseStatus.submitted,
            record=record,
            user=owner,
        )

        webhook = await WebhookFactory.create(events=[ResponseEvent.created, ResponseEvent.updated])

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "values": {
                            "text-question": {
                                "value": "Updated value",
                            },
                        },
                        "status": ResponseStatus.submitted,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200

        event = await build_response_event(db, ResponseEvent.updated, response)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == ResponseEvent.updated
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)

    async def test_create_current_user_responses_bulk_enqueue_webhook_record_updated_event(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            },
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        webhook = await WebhookFactory.create(events=[RecordEvent.updated])

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "values": {
                            "text-question": {
                                "value": "Created value",
                            },
                        },
                        "status": ResponseStatus.submitted,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200

        event = await build_record_event(db, RecordEvent.updated, record)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.updated
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)

    async def test_create_current_user_responses_bulk_enqueue_webhook_record_completed_event(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            },
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        webhook = await WebhookFactory.create(events=[RecordEvent.completed])

        resp = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "values": {
                            "text-question": {
                                "value": "Created value",
                            },
                        },
                        "status": ResponseStatus.submitted,
                        "record_id": str(record.id),
                    },
                ],
            },
        )

        assert resp.status_code == 200

        event = await build_record_event(db, RecordEvent.completed, record)

        assert HIGH_QUEUE.count == 1
        assert HIGH_QUEUE.jobs[0].args[0] == webhook.id
        assert HIGH_QUEUE.jobs[0].args[1] == RecordEvent.completed
        assert HIGH_QUEUE.jobs[0].args[3] == jsonable_encoder(event.data)
