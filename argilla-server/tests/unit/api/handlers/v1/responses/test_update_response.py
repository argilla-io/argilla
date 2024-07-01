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
from httpx import AsyncClient

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from argilla_server.enums import ResponseStatus, DatasetDistributionStrategy, RecordStatus
from argilla_server.models import Response, User

from tests.factories import DatasetFactory, RecordFactory, ResponseFactory, SpanQuestionFactory, TextQuestionFactory


@pytest.mark.asyncio
class TestUpdateResponse:
    def url(self, response_id: UUID) -> str:
        return f"/api/v1/responses/{response_id}"

    async def test_update_response_for_span_question(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)
        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values={
                "span-question": {
                    "value": [
                        {"label": "label-a", "start": 0, "end": 1},
                    ]
                }
            },
            user=owner,
            record=record,
        )

        body_json = {
            "status": ResponseStatus.submitted,
            "values": {
                "span-question": {
                    "value": [
                        {"label": "label-a", "start": 0, "end": 1},
                        {"label": "label-b", "start": 2, "end": 3},
                        {"label": "label-c", "start": 4, "end": 5},
                    ]
                },
            },
        }

        resp = await async_client.put(self.url(response.id), headers=owner_auth_header, json=body_json)

        assert resp.status_code == 200
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == body_json["values"]

        resp_json = resp.json()
        assert resp_json == {
            "id": str(response.id),
            "status": ResponseStatus.submitted,
            "values": {
                "span-question": {
                    "value": [
                        {"label": "label-a", "start": 0, "end": 1},
                        {"label": "label-b", "start": 2, "end": 3},
                        {"label": "label-c", "start": 4, "end": 5},
                    ]
                },
            },
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": response.inserted_at.isoformat(),
            "updated_at": datetime.fromisoformat(resp_json["updated_at"]).isoformat(),
        }

    async def test_update_response_for_span_question_with_additional_value_attributes(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)
        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values={
                "span-question": {
                    "value": [
                        {"label": "label-a", "start": 0, "end": 1},
                    ]
                }
            },
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 1, "ignored": "value"},
                            {"label": "label-b", "start": 2, "end": 3, "ignored": "value"},
                            {"label": "label-c", "start": 4, "end": 5},
                        ],
                    },
                },
            },
        )

        expected_values = {
            "span-question": {
                "value": [
                    {"label": "label-a", "start": 0, "end": 1},
                    {"label": "label-b", "start": 2, "end": 3},
                    {"label": "label-c", "start": 4, "end": 5},
                ],
            },
        }

        assert resp.status_code == 200
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == expected_values

        resp_json = resp.json()
        assert resp_json == {
            "id": str(response.id),
            "status": ResponseStatus.submitted,
            "values": expected_values,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": response.inserted_at.isoformat(),
            "updated_at": datetime.fromisoformat(resp_json["updated_at"]).isoformat(),
        }

    async def test_update_response_for_span_question_with_empty_value(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)
        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values={
                "span-question": {
                    "value": [
                        {"label": "label-a", "start": 0, "end": 1},
                        {"label": "label-b", "start": 2, "end": 3},
                        {"label": "label-c", "start": 4, "end": 5},
                    ]
                }
            },
            user=owner,
            record=record,
        )

        body_json = {
            "status": ResponseStatus.submitted,
            "values": {
                "span-question": {
                    "value": [],
                },
            },
        }

        resp = await async_client.put(self.url(response.id), headers=owner_auth_header, json=body_json)

        assert resp.status_code == 200
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == body_json["values"]

        resp_json = resp.json()
        assert resp_json == {
            "id": str(response.id),
            "status": ResponseStatus.submitted,
            "values": {
                "span-question": {
                    "value": [],
                },
            },
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": response.inserted_at.isoformat(),
            "updated_at": datetime.fromisoformat(resp_json["updated_at"]).isoformat(),
        }

    async def test_update_response_for_span_question_with_record_not_providing_required_field(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"other-field": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 0, "end": 1}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert resp.json() == {"detail": "span question requires record to have field `field-a`"}

        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_invalid_value(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [{"label": "label-a", "start": 0, "end": 1}],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [
                            {"label": "label-a", "start": 0, "end": 1},
                            {"invalid": "value"},
                        ],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_start_greater_than_expected(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 5, "end": 6}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert resp.json() == {
            "detail": "span question response value `start` must have a value lower than record field `field-a` length that is `5`"
        }

        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_end_greater_than_expected(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 4, "end": 6}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert resp.json() == {
            "detail": "span question response value `end` must have a value lower or equal than record field `field-a` length that is `5`"
        }

        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_invalid_start(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": -1, "end": 1}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_invalid_end(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 0, "end": 0}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_equal_start_and_end(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 1, "end": 1}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_end_smaller_than_start(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-a", "start": 3, "end": 2}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_for_span_question_with_non_existent_label(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await SpanQuestionFactory.create(name="span-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)

        response_values = {
            "span-question": {
                "value": [],
            }
        }

        response = await ResponseFactory.create(
            status=ResponseStatus.submitted,
            values=response_values,
            user=owner,
            record=record,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "status": ResponseStatus.submitted,
                "values": {
                    "span-question": {
                        "value": [{"label": "label-non-existent", "start": 1, "end": 2}],
                    },
                },
            },
        )

        assert resp.status_code == 422
        assert resp.json() == {
            "detail": "undefined label 'label-non-existent' for span question.\nValid labels are: ['label-a', 'label-b', 'label-c']"
        }

        assert (await db.execute(select(Response).filter_by(id=response.id))).scalar_one().values == response_values

    async def test_update_response_updates_record_status_to_completed(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            },
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset)
        response = await ResponseFactory.create(record=record, status=ResponseStatus.draft)

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={
                "values": {
                    "text-question": {
                        "value": "text question updated response",
                    },
                },
                "status": ResponseStatus.submitted,
            },
        )

        assert resp.status_code == 200
        assert record.status == RecordStatus.completed

    async def test_update_response_updates_record_status_to_pending(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            },
        )

        await TextQuestionFactory.create(name="text-question", dataset=dataset)

        record = await RecordFactory.create(fields={"field-a": "Hello"}, dataset=dataset, status=RecordStatus.completed)
        response = await ResponseFactory.create(
            values={
                "text-question": {
                    "value": "text question response",
                },
            },
            record=record,
            status=ResponseStatus.submitted,
        )

        resp = await async_client.put(
            self.url(response.id),
            headers=owner_auth_header,
            json={"status": ResponseStatus.draft},
        )

        assert resp.status_code == 200
        assert record.status == RecordStatus.pending
