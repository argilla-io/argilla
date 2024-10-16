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
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.enums import (
    DatasetStatus,
    QuestionType,
    ResponseStatus,
    SuggestionType,
    RecordStatus,
    DatasetDistributionStrategy,
)
from argilla_server.models.database import Record, Response, Suggestion, User
from tests.factories import (
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    SpanQuestionFactory,
    TextFieldFactory,
    ImageFieldFactory,
    TextQuestionFactory,
    ChatFieldFactory,
    CustomFieldFactory,
    AnnotatorFactory,
)


@pytest.mark.asyncio
class TestCreateDatasetRecordsBulk:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_create_dataset_records_bulk(
        self, db: AsyncSession, async_client: AsyncClient, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextFieldFactory.create(name="response", dataset=dataset)
        await ImageFieldFactory.create(name="image", dataset=dataset)

        text_question = await TextQuestionFactory.create(name="text-question", dataset=dataset)

        label_selection_question = await LabelSelectionQuestionFactory.create(
            name="label-selection-question",
            settings={
                "type": QuestionType.label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                ],
            },
            dataset=dataset,
        )

        multi_label_selection_question = await MultiLabelSelectionQuestionFactory.create(
            name="multi-label-selection-question",
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
            },
            dataset=dataset,
        )

        rating_question = await RatingQuestionFactory.create(
            name="rating-question",
            settings={
                "type": QuestionType.rating,
                "options": [
                    {"value": 1},
                    {"value": 2},
                    {"value": 3},
                ],
            },
            dataset=dataset,
        )

        ranking_question = await RankingQuestionFactory.create(
            name="ranking-question",
            settings={
                "type": QuestionType.ranking,
                "options": [
                    {"value": "ranking-a", "text": "Ranking A", "description": "Ranking A description"},
                    {"value": "ranking-b", "text": "Ranking B", "description": "Ranking B description"},
                ],
            },
            dataset=dataset,
        )

        span_question = await SpanQuestionFactory.create(
            name="span-question",
            settings={
                "type": QuestionType.span,
                "field": "response",
                "options": [
                    {"value": "thing", "text": "Thing", "description": "Thing description"},
                    {"value": "place", "text": "Place", "description": "Place description"},
                ],
            },
            dataset=dataset,
        )

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                            "image": "https://argilla.io/image.jpeg",
                        },
                        "external_id": "1",
                        "responses": [
                            {
                                "status": ResponseStatus.submitted,
                                "values": {
                                    "text-question": {
                                        "value": "response to text question",
                                    },
                                    "label-selection-question": {
                                        "value": "label-b",
                                    },
                                    "multi-label-selection-question": {
                                        "value": [
                                            "label-a",
                                            "label-c",
                                        ]
                                    },
                                    "rating-question": {
                                        "value": 3,
                                    },
                                    "ranking-question": {
                                        "value": [
                                            {"value": "ranking-a", "rank": 1},
                                            {"value": "ranking-b", "rank": 2},
                                        ],
                                    },
                                    "span-question": {
                                        "value": [
                                            {"label": "thing", "start": 0, "end": 6},
                                            {"label": "place", "start": 8, "end": 12},
                                        ],
                                    },
                                },
                                "user_id": str(owner.id),
                            },
                        ],
                        "suggestions": [
                            {
                                "type": SuggestionType.model,
                                "score": 0.5,
                                "value": "suggestion to text question",
                                "question_id": str(text_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": 0.9,
                                "value": "label-a",
                                "question_id": str(label_selection_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": [1.0, 0.1],
                                "value": [
                                    "label-a",
                                    "label-b",
                                ],
                                "question_id": str(multi_label_selection_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": 0.9,
                                "value": 1,
                                "question_id": str(rating_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": [0.2, 0.5],
                                "value": [
                                    {"value": "ranking-a", "rank": 1},
                                    {"value": "ranking-b", "rank": 2},
                                ],
                                "question_id": str(ranking_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": [0.5, 0.9],
                                "value": [
                                    {"label": "thing", "start": 0, "end": 5},
                                    {"label": "place", "start": 6, "end": 8},
                                ],
                                "question_id": str(span_question.id),
                            },
                        ],
                    },
                ],
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 1
        assert (await db.execute(select(func.count(Response.id)))).scalar_one() == 1
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar_one() == 6

    @pytest.mark.parametrize(
        "web_url",
        [
            "http://argilla.io/image.jpeg",
            "http://argilla.io/path/to/image.jpeg",
            "https://argilla.io/image.jpeg",
            "https://argilla.io/path/to/image.jpeg",
        ],
    )
    async def test_create_dataset_records_bulk_with_web_url_image_field(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict, web_url: str
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "image": web_url,
                        },
                    },
                ],
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 1

    @pytest.mark.parametrize(
        "data_url",
        [
            "data:image/jpeg;base64,/9j/4QC8RXhpZgAASUkqAAgAAAAGABIBAwABAAAA",
            "data:image/webp;base64,UklGRhgCAABXRUJQVlA4WAoAAAAIAAAAHwAAFwA",
        ],
    )
    async def test_create_dataset_records_bulk_with_data_url_image_field(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict, data_url: str
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "image": data_url,
                        },
                    },
                ],
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 1

    @pytest.mark.parametrize(
        "invalid_url",
        [
            "http://argilla.io",
            "https://argilla.io",
            "http:/argilla.io",
            "https:/argilla.io",
            "invalid-url",
            "data:",
        ],
    )
    async def test_create_dataset_records_bulk_with_invalid_image_field_url(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict, invalid_url: str
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "image": invalid_url,
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"record at position 0 is not valid because image field 'image' has an invalid URL value",
        }

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_image_field_web_url_exceeding_maximum_length(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "image": f"https://argilla.io/{'a' * 2038}.jpeg",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"record at position 0 is not valid because image field 'image' value is exceeding the maximum length of 2038 characters for Web URLs",
        }

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_image_field_data_url_using_invalid_mime_type(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "image": "data:image/invalid;base64,UklGRhgCAABXRUJQVlA4WAoAAAAIAAAAHwAAFwA",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"record at position 0 is not valid because image field 'image' value is using an unsupported MIME type, supported MIME types are: ['image/avif', 'image/gif', 'image/ico', 'image/jpeg', 'image/jpg', 'image/png', 'image/svg', 'image/webp']",
        }

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_image_field_data_url_exceeding_maximum_length(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "image": f"data:image/jpeg;base64,{'a' * 5_000_000}",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"record at position 0 is not valid because image field 'image' value is exceeding the maximum length of 5000000 characters for Data URLs",
        }

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_chat_field(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ChatFieldFactory.create(name="chat", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "chat": [
                                {
                                    "role": "user",
                                    "content": "Hello!",
                                }
                            ],
                        },
                    },
                ],
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 1

    async def test_create_dataset_records_bulk_with_chat_field_with_value_exceeding_maximum_length(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ChatFieldFactory.create(name="chat", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "chat": [
                                {
                                    "role": "user",
                                    "content": "a",
                                }
                            ]
                            * 1000,
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_chat_field_with_non_dicts(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ChatFieldFactory.create(name="chat", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "chat": "invalid",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_chat_field_without_role_key(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ChatFieldFactory.create(name="chat", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "chat": [
                                {
                                    "content": "Hello!",
                                }
                            ],
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_chat_field_without_content_key(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ChatFieldFactory.create(name="chat", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "chat": [
                                {
                                    "role": "user",
                                }
                            ],
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body", "items", 0, "fields"],
                            "msg": "Error parsing chat field 'chat': [{'loc': ('content',), 'msg': 'field required', 'type': 'value_error.missing'}]",
                            "type": "value_error",
                        }
                    ]
                },
            }
        }
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

    async def test_create_dataset_records_bulk_with_custom_field_values(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await CustomFieldFactory.create(name="custom", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "custom": {"a": 1, "b": 2},
                        },
                    },
                    {
                        "fields": {
                            "custom": {"c": 1, "b": 2},
                        },
                    },
                    {
                        "fields": {
                            "custom": {"a": 1},
                        },
                    },
                ],
            },
        )

        assert response.status_code == 201, response.json()
        records = (await db.execute(select(Record))).scalars().all()
        assert len(records) == 3
        assert records[0].fields["custom"] == {"a": 1, "b": 2}
        assert records[1].fields["custom"] == {"c": 1, "b": 2}
        assert records[2].fields["custom"] == {"a": 1}

    async def test_create_dataset_records_bulk_with_wrong_custom_field_value(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await CustomFieldFactory.create(name="custom", dataset=dataset)
        await LabelSelectionQuestionFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "custom": "invalid",
                        },
                    },
                ],
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 0

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
