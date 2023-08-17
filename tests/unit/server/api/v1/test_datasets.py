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
from typing import TYPE_CHECKING, List, Optional, Tuple, Type
from unittest.mock import ANY, MagicMock
from uuid import UUID, uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.apis.v1.handlers.datasets import LIST_DATASET_RECORDS_LIMIT_DEFAULT
from argilla.server.enums import ResponseStatusFilter
from argilla.server.models import (
    Dataset,
    DatasetStatus,
    Field,
    Question,
    Record,
    Response,
    ResponseStatus,
    Suggestion,
    User,
    UserRole,
    Workspace,
)
from argilla.server.schemas.v1.datasets import (
    DATASET_GUIDELINES_MAX_LENGTH,
    DATASET_NAME_MAX_LENGTH,
    FIELD_CREATE_NAME_MAX_LENGTH,
    FIELD_CREATE_TITLE_MAX_LENGTH,
    QUESTION_CREATE_DESCRIPTION_MAX_LENGTH,
    QUESTION_CREATE_NAME_MAX_LENGTH,
    QUESTION_CREATE_TITLE_MAX_LENGTH,
    RATING_OPTIONS_MAX_ITEMS,
    RATING_OPTIONS_MIN_ITEMS,
    RECORDS_CREATE_MAX_ITEMS,
    RECORDS_CREATE_MIN_ITEMS,
    VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH,
    VALUE_TEXT_OPTION_TEXT_MAX_LENGTH,
    VALUE_TEXT_OPTION_VALUE_MAX_LENGTH,
    RecordInclude,
)
from argilla.server.search_engine import (
    Query,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    TextQuery,
    UserResponseStatusFilter,
)
from sqlalchemy import func, select

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    FieldFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    QuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    SuggestionFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestSuiteDatasets:
    async def test_list_current_user_datasets(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset_a = await DatasetFactory.create(name="dataset-a")
        dataset_b = await DatasetFactory.create(name="dataset-b", guidelines="guidelines")
        dataset_c = await DatasetFactory.create(name="dataset-c", status=DatasetStatus.ready)

        response = await async_client.get("/api/v1/me/datasets", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(dataset_a.id),
                    "name": "dataset-a",
                    "guidelines": None,
                    "status": "draft",
                    "workspace_id": str(dataset_a.workspace_id),
                    "inserted_at": dataset_a.inserted_at.isoformat(),
                    "updated_at": dataset_a.updated_at.isoformat(),
                },
                {
                    "id": str(dataset_b.id),
                    "name": "dataset-b",
                    "guidelines": "guidelines",
                    "status": "draft",
                    "workspace_id": str(dataset_b.workspace_id),
                    "inserted_at": dataset_b.inserted_at.isoformat(),
                    "updated_at": dataset_b.updated_at.isoformat(),
                },
                {
                    "id": str(dataset_c.id),
                    "name": "dataset-c",
                    "guidelines": None,
                    "status": "ready",
                    "workspace_id": str(dataset_c.workspace_id),
                    "inserted_at": dataset_c.inserted_at.isoformat(),
                    "updated_at": dataset_c.updated_at.isoformat(),
                },
            ]
        }

    async def test_list_current_user_datasets_without_authentication(self, async_client: "AsyncClient"):
        response = await async_client.get("/api/v1/me/datasets")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_current_user_datasets_as_restricted_user_role(
        self, async_client: "AsyncClient", role: UserRole
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        await DatasetFactory.create(name="dataset-a", workspace=workspace)
        await DatasetFactory.create(name="dataset-b", workspace=workspace)
        await DatasetFactory.create(name="dataset-c")

        response = await async_client.get("/api/v1/me/datasets", headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 200

        response_body = response.json()
        assert [dataset["name"] for dataset in response_body["items"]] == ["dataset-a", "dataset-b"]

    async def test_list_dataset_fields(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        text_field_a = await TextFieldFactory.create(
            name="text-field-a", title="Text Field A", required=True, dataset=dataset
        )
        text_field_b = await TextFieldFactory.create(name="text-field-b", title="Text Field B", dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await TextFieldFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(text_field_a.id),
                    "name": "text-field-a",
                    "title": "Text Field A",
                    "required": True,
                    "settings": {"type": "text", "use_markdown": False},
                    "inserted_at": text_field_a.inserted_at.isoformat(),
                    "updated_at": text_field_a.updated_at.isoformat(),
                },
                {
                    "id": str(text_field_b.id),
                    "name": "text-field-b",
                    "title": "Text Field B",
                    "required": False,
                    "settings": {"type": "text", "use_markdown": False},
                    "inserted_at": text_field_b.inserted_at.isoformat(),
                    "updated_at": text_field_b.updated_at.isoformat(),
                },
            ],
        }

    async def test_list_dataset_fields_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/fields")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_dataset_fields_as_restricted_user_role(self, async_client: "AsyncClient", role: UserRole):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)
        await TextFieldFactory.create(name="text-field-a", dataset=dataset)
        await TextFieldFactory.create(name="text-field-b", dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await TextFieldFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/fields", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [field["name"] for field in response_body["items"]] == ["text-field-a", "text-field-b"]

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_dataset_fields_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/fields", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403

    async def test_list_dataset_fields_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{uuid4()}/fields", headers=owner_auth_header)

        assert response.status_code == 404

    async def test_list_dataset_questions(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        text_question = await TextQuestionFactory.create(
            name="text-question",
            title="Text Question",
            required=True,
            dataset=dataset,
        )
        rating_question = await RatingQuestionFactory.create(
            name="rating-question",
            title="Rating Question",
            description="Rating Description",
            dataset=dataset,
        )
        await TextQuestionFactory.create()
        await RatingQuestionFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(text_question.id),
                    "name": "text-question",
                    "title": "Text Question",
                    "description": "Question Description",
                    "required": True,
                    "settings": {"type": "text", "use_markdown": False},
                    "inserted_at": text_question.inserted_at.isoformat(),
                    "updated_at": text_question.updated_at.isoformat(),
                },
                {
                    "id": str(rating_question.id),
                    "name": "rating-question",
                    "title": "Rating Question",
                    "description": "Rating Description",
                    "required": False,
                    "settings": {
                        "type": "rating",
                        "options": [
                            {"value": 1},
                            {"value": 2},
                            {"value": 3},
                            {"value": 4},
                            {"value": 5},
                            {"value": 6},
                            {"value": 7},
                            {"value": 8},
                            {"value": 9},
                            {"value": 10},
                        ],
                    },
                    "inserted_at": rating_question.inserted_at.isoformat(),
                    "updated_at": rating_question.updated_at.isoformat(),
                },
            ]
        }

    @pytest.mark.parametrize(
        "QuestionFactory, settings",
        [
            (RatingQuestionFactory, {"options": [{"value": 1}, {"value": 2}, {"value": 2}]}),
            (
                LabelSelectionQuestionFactory,
                {
                    "options": [
                        {"value": "a", "text": "a", "description": "a"},
                        {"value": "b", "text": "b", "description": "b"},
                        {"value": "b", "text": "b", "description": "b"},
                    ],
                    "visible_options": None,
                },
            ),
            (
                MultiLabelSelectionQuestionFactory,
                {
                    "options": [
                        {"value": "a", "text": "a", "description": "a"},
                        {"value": "b", "text": "b", "description": "b"},
                        {"value": "b", "text": "b", "description": "b"},
                    ],
                    "visible_options": None,
                },
            ),
        ],
    )
    async def test_list_dataset_questions_with_duplicate_values(
        self,
        async_client: "AsyncClient",
        owner_auth_header: dict,
        QuestionFactory: Type[QuestionFactory],
        settings: dict,
    ):
        dataset = await DatasetFactory.create()
        question = await QuestionFactory.create(dataset=dataset, settings=settings)

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header)
        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(question.id),
                    "name": question.name,
                    "title": question.title,
                    "description": question.description,
                    "required": question.required,
                    "settings": {"type": QuestionFactory.settings["type"], **settings},
                    "inserted_at": question.inserted_at.isoformat(),
                    "updated_at": question.updated_at.isoformat(),
                }
            ]
        }

    async def test_list_dataset_questions_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/questions")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_dataset_questions_as_restricted_user(self, async_client: "AsyncClient", role: UserRole):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)
        await TextQuestionFactory.create(name="text-question", dataset=dataset)
        await RatingQuestionFactory.create(name="rating-question", dataset=dataset)
        await TextQuestionFactory.create()
        await RatingQuestionFactory.create()

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/questions", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [question["name"] for question in response_body["items"]] == ["text-question", "rating-question"]

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_dataset_questions_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/questions", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403

    async def test_list_dataset_questions_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{uuid4()}/questions", headers=owner_auth_header)

        assert response.status_code == 404

    async def test_list_dataset_records(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_b = await RecordFactory.create(
            fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset
        )
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"record_a": "value_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"record_b": "value_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"record_c": "value_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

    @pytest.mark.parametrize(
        "includes",
        [[RecordInclude.responses], [RecordInclude.suggestions], [RecordInclude.responses, RecordInclude.suggestions]],
    )
    async def test_list_dataset_records_with_include(
        self, async_client: "AsyncClient", owner: User, owner_auth_header: dict, includes: List[RecordInclude]
    ):
        workspace = await WorkspaceFactory.create()
        dataset, questions, records, responses, suggestions = await self.create_dataset_with_user_responses(
            owner, workspace
        )
        record_a, record_b, record_c = records
        response_a_user, response_b_user = responses[1], responses[3]
        suggestion_a, suggestion_b = suggestions

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        expected = {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"input": "value_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"input": "value_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"input": "value_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

        if RecordInclude.responses in includes:
            expected["items"][0]["responses"] = [
                {
                    "id": str(response_a_user.id),
                    "values": None,
                    "status": "discarded",
                    "user_id": str(owner.id),
                    "inserted_at": response_a_user.inserted_at.isoformat(),
                    "updated_at": response_a_user.updated_at.isoformat(),
                }
            ]
            expected["items"][1]["responses"] = [
                {
                    "id": str(response_b_user.id),
                    "values": {
                        "input_ok": {"value": "no"},
                        "output_ok": {"value": "no"},
                    },
                    "status": "submitted",
                    "user_id": str(owner.id),
                    "inserted_at": response_b_user.inserted_at.isoformat(),
                    "updated_at": response_b_user.updated_at.isoformat(),
                },
            ]
            expected["items"][2]["responses"] = []

        if RecordInclude.suggestions in includes:
            expected["items"][0]["suggestions"] = [
                {
                    "id": str(suggestion_a.id),
                    "value": "option-1",
                    "score": None,
                    "agent": None,
                    "type": None,
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][1]["suggestions"] = [
                {
                    "id": str(suggestion_b.id),
                    "value": "option-2",
                    "score": 0.75,
                    "agent": "unit-test-agent",
                    "type": "model",
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][2]["suggestions"] = []

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params={"include": RecordInclude.responses.value},
            headers=owner_auth_header,
        )

        assert response.status_code == 200

    async def test_list_dataset_records_with_offset(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 2}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    async def test_list_dataset_records_with_limit(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]

    async def test_list_dataset_records_with_offset_and_limit(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 1, "limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    async def test_list_dataset_records_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/records")

        assert response.status_code == 401

    async def test_list_dataset_records_as_admin(self, async_client: "AsyncClient"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)

        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: admin.api_key}
        )
        assert response.status_code == 200

    async def test_list_dataset_records_as_annotator(self, async_client: "AsyncClient"):
        workspace = await WorkspaceFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)

        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )
        assert response.status_code == 403

    async def create_dataset_with_user_responses(
        self, user: User, workspace: Workspace
    ) -> Tuple[Dataset, List[Question], List[Record], List[Response], List[Suggestion]]:
        dataset = await DatasetFactory.create(workspace=workspace)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)

        annotator = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        questions = [
            await LabelSelectionQuestionFactory.create(dataset=dataset),
            await TextQuestionFactory.create(name="input_ok", dataset=dataset),
            await TextQuestionFactory.create(name="output_ok", dataset=dataset),
        ]

        records = [
            await RecordFactory.create(fields={"input": "input_a", "output": "output_a"}, dataset=dataset),
            await RecordFactory.create(
                fields={"input": "input_b", "output": "output_b"}, metadata_={"unit": "test"}, dataset=dataset
            ),
            await RecordFactory.create(
                fields={"input": "input_c", "output": "output_c"}, dataset=dataset, inserted_at=datetime.utcnow()
            ),
        ]

        responses = [
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
                record=records[0],
                user=annotator,
            ),
            await ResponseFactory.create(status="discarded", record=records[0], user=user),
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "no"},
                },
                record=records[1],
                user=annotator,
            ),
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "no"},
                    "output_ok": {"value": "no"},
                },
                record=records[1],
                user=user,
            ),
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
                record=records[1],
            ),
        ]

        # Add some responses from other users
        await ResponseFactory.create_batch(10, record=records[0], status=ResponseStatus.submitted)

        suggestions = [
            await SuggestionFactory.create(record=records[0], question=questions[0], value="option-1"),
            await SuggestionFactory.create(
                record=records[1],
                question=questions[0],
                value="option-2",
                score=0.75,
                agent="unit-test-agent",
                type="model",
            ),
        ]

        return dataset, questions, records, responses, suggestions

    async def test_list_current_user_dataset_records(
        self, async_client: "AsyncClient", owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)
        record_a, record_b, record_c = records

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"input": "input_a", "output": "output_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"input": "input_b", "output": "output_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"input": "input_c", "output": "output_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin, UserRole.owner])
    @pytest.mark.parametrize(
        "includes",
        [[RecordInclude.responses], [RecordInclude.suggestions], [RecordInclude.responses, RecordInclude.suggestions]],
    )
    async def test_list_current_user_dataset_records_with_include(
        self, async_client: "AsyncClient", role: UserRole, includes: List[RecordInclude]
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)
        dataset, questions, records, responses, suggestions = await self.create_dataset_with_user_responses(
            user, workspace
        )
        record_a, record_b, record_c = records
        response_a_user, response_b_user = responses[1], responses[3]
        suggestion_a, suggestion_b = suggestions

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        params = [("include", include.value) for include in includes]
        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", params=params, headers={API_KEY_HEADER_NAME: user.api_key}
        )

        expected = {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"input": "input_a", "output": "output_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"input": "input_b", "output": "output_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"input": "input_c", "output": "output_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

        if RecordInclude.responses in includes:
            expected["items"][0]["responses"] = [
                {
                    "id": str(response_a_user.id),
                    "values": None,
                    "status": "discarded",
                    "user_id": str(user.id),
                    "inserted_at": response_a_user.inserted_at.isoformat(),
                    "updated_at": response_a_user.updated_at.isoformat(),
                }
            ]
            expected["items"][1]["responses"] = [
                {
                    "id": str(response_b_user.id),
                    "values": {
                        "input_ok": {"value": "no"},
                        "output_ok": {"value": "no"},
                    },
                    "status": "submitted",
                    "user_id": str(user.id),
                    "inserted_at": response_b_user.inserted_at.isoformat(),
                    "updated_at": response_b_user.updated_at.isoformat(),
                },
            ]
            expected["items"][2]["responses"] = []

        if RecordInclude.suggestions in includes:
            expected["items"][0]["suggestions"] = [
                {
                    "id": str(suggestion_a.id),
                    "value": "option-1",
                    "score": None,
                    "agent": None,
                    "type": None,
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][1]["suggestions"] = [
                {
                    "id": str(suggestion_b.id),
                    "value": "option-2",
                    "score": 0.75,
                    "agent": "unit-test-agent",
                    "type": "model",
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][2]["suggestions"] = []

        assert response.status_code == 200
        assert response.json() == expected

    async def test_list_current_user_dataset_records_with_offset(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 2}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    async def test_list_current_user_dataset_records_with_limit(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]

    async def test_list_current_user_dataset_records_with_offset_and_limit(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 1, "limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    async def create_records_with_response(
        self,
        num_records: int,
        dataset: Dataset,
        user: User,
        response_status: ResponseStatus,
        response_values: Optional[dict] = None,
    ):
        for record in await RecordFactory.create_batch(size=num_records, dataset=dataset):
            await ResponseFactory.create(record=record, user=user, values=response_values, status=response_status)

    @pytest.mark.parametrize("response_status_filter", ["missing", "discarded", "submitted", "draft"])
    async def test_list_current_user_dataset_records_with_response_status_filter(
        self, async_client: "AsyncClient", owner: "User", owner_auth_header: dict, response_status_filter: str
    ):
        num_responses_per_status = 10
        response_values = {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}}

        dataset = await DatasetFactory.create()
        # missing responses
        await RecordFactory.create_batch(size=num_responses_per_status, dataset=dataset)
        # discarded responses
        await self.create_records_with_response(num_responses_per_status, dataset, owner, ResponseStatus.discarded)
        # submitted responses
        await self.create_records_with_response(
            num_responses_per_status, dataset, owner, ResponseStatus.submitted, response_values
        )
        # drafted responses
        await self.create_records_with_response(
            num_responses_per_status, dataset, owner, ResponseStatus.draft, response_values
        )

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records?response_status={response_status_filter}&include=responses",
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json["items"]) == num_responses_per_status

        if response_status_filter == "missing":
            assert all([len(record["responses"]) == 0 for record in response_json["items"]])
        else:
            assert all(
                [record["responses"][0]["status"] == response_status_filter for record in response_json["items"]]
            )

    async def test_list_current_user_dataset_records_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/me/datasets/{dataset.id}/records")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_list_current_user_dataset_records_as_restricted_user(
        self, async_client: "AsyncClient", role: UserRole
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)
        dataset = await DatasetFactory.create(workspace=workspace)
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_b = await RecordFactory.create(
            fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset
        )
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)
        expected_records = [record_a, record_b, record_c]

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200

        response_items = response.json()["items"]

        for expected_record in expected_records:
            found_items = [item for item in response_items if item["id"] == str(expected_record.id)]
            assert found_items, expected_record

            assert found_items[0] == {
                "id": str(expected_record.id),
                "fields": expected_record.fields,
                "metadata": expected_record.metadata_,
                "external_id": expected_record.external_id,
                "inserted_at": expected_record.inserted_at.isoformat(),
                "updated_at": expected_record.updated_at.isoformat(),
            }

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_current_user_dataset_records_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403

    async def test_list_current_user_dataset_records_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/me/datasets/{uuid4()}/records", headers=owner_auth_header)

        assert response.status_code == 404

    async def test_get_dataset(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create(name="dataset")

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(dataset.id),
            "name": "dataset",
            "guidelines": None,
            "status": "draft",
            "workspace_id": str(dataset.workspace_id),
            "inserted_at": dataset.inserted_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
        }

    async def test_get_dataset_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_get_dataset_as_restricted_user(self, async_client: "AsyncClient", role: UserRole):
        dataset = await DatasetFactory.create(name="dataset")
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 200
        assert response.json()["name"] == "dataset"

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_get_dataset_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 403

    async def test_get_dataset_with_nonexistent_dataset_id(self, async_client: "AsyncClient", owner_auth_header: dict):
        await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{uuid4()}", headers=owner_auth_header)

        assert response.status_code == 404

    async def test_get_current_user_dataset_metrics(
        self, async_client: "AsyncClient", owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        record_d = await RecordFactory.create(dataset=dataset)
        await RecordFactory.create_batch(3, dataset=dataset)
        await ResponseFactory.create(record=record_a, user=owner)
        await ResponseFactory.create(record=record_b, user=owner, status=ResponseStatus.discarded)
        await ResponseFactory.create(record=record_c, user=owner, status=ResponseStatus.discarded)
        await ResponseFactory.create(record=record_d, user=owner, status=ResponseStatus.draft)

        other_dataset = await DatasetFactory.create()
        other_record_a = await RecordFactory.create(dataset=other_dataset)
        other_record_b = await RecordFactory.create(dataset=other_dataset)
        other_record_c = await RecordFactory.create(dataset=other_dataset)
        await RecordFactory.create_batch(2, dataset=other_dataset)
        await ResponseFactory.create(record=other_record_a, user=owner)
        await ResponseFactory.create(record=other_record_b)
        await ResponseFactory.create(record=other_record_c, status=ResponseStatus.discarded)

        response = await async_client.get(f"/api/v1/me/datasets/{dataset.id}/metrics", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "records": {
                "count": 7,
            },
            "responses": {
                "count": 4,
                "submitted": 1,
                "discarded": 2,
                "draft": 1,
            },
        }

    async def test_get_current_user_dataset_metrics_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/me/datasets/{dataset.id}/metrics")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_get_current_user_dataset_metrics_as_annotator(self, async_client: "AsyncClient", role: UserRole):
        dataset = await DatasetFactory.create()
        user = await AnnotatorFactory.create(workspaces=[dataset.workspace], role=role)
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        record_d = await RecordFactory.create(dataset=dataset)
        await RecordFactory.create_batch(2, dataset=dataset)
        await ResponseFactory.create(record=record_a, user=user)
        await ResponseFactory.create(record=record_b, user=user)
        await ResponseFactory.create(record=record_c, user=user, status=ResponseStatus.discarded)
        await ResponseFactory.create(record=record_d, user=user, status=ResponseStatus.draft)

        other_dataset = await DatasetFactory.create()
        other_record_a = await RecordFactory.create(dataset=other_dataset)
        other_record_b = await RecordFactory.create(dataset=other_dataset)
        other_record_c = await RecordFactory.create(dataset=other_dataset)
        await RecordFactory.create_batch(3, dataset=other_dataset)
        await ResponseFactory.create(record=other_record_a, user=user)
        await ResponseFactory.create(record=other_record_b)
        await ResponseFactory.create(record=other_record_c, status=ResponseStatus.discarded)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/metrics", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200
        assert response.json() == {
            "records": {"count": 6},
            "responses": {"count": 4, "submitted": 2, "discarded": 1, "draft": 1},
        }

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_get_current_user_dataset_metrics_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/metrics", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403

    async def test_get_current_user_dataset_metrics_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/me/datasets/{uuid4()}/metrics", headers=owner_auth_header)

        assert response.status_code == 404

    async def test_create_dataset(self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict):
        workspace = await WorkspaceFactory.create()
        dataset_json = {"name": "name", "guidelines": "guidelines", "workspace_id": str(workspace.id)}

        response = await async_client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 1

        await db.refresh(workspace)

        response_body = response.json()
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 1
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "name": "name",
            "guidelines": "guidelines",
            "status": "draft",
            "workspace_id": str(workspace.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    async def test_create_dataset_with_invalid_length_guidelines(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset_json = {
            "name": "name",
            "guidelines": "a" * (DATASET_GUIDELINES_MAX_LENGTH + 1),
            "workspace_id": str(workspace.id),
        }

        response = await async_client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "dataset_json",
        [
            {"name": ""},
            {"name": "123$abc"},
            {"name": "unit@test"},
            {"name": "-test-dataset"},
            {"name": "_test-dataset"},
            {"name": "a" * (DATASET_NAME_MAX_LENGTH + 1)},
            {"name": "test-dataset", "guidelines": ""},
            {"name": "test-dataset", "guidelines": "a" * (DATASET_GUIDELINES_MAX_LENGTH + 1)},
        ],
    )
    async def test_create_dataset_with_invalid_settings(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, dataset_json: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset_json.update({"workspace_id": str(workspace.id)})

        response = await async_client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 0

    async def test_create_dataset_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        workspace = await WorkspaceFactory.create()
        dataset_json = {"name": "name", "workspace_id": str(workspace.id)}

        response = await async_client.post("/api/v1/datasets", json=dataset_json)

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 0

    async def test_create_dataset_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])

        dataset_json = {"name": "name", "workspace_id": str(workspace.id)}
        response = await async_client.post(
            "/api/v1/datasets", headers={API_KEY_HEADER_NAME: admin.api_key}, json=dataset_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 1

    async def test_create_dataset_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        workspace = await WorkspaceFactory.create()
        dataset_json = {"name": "name", "workspace_id": str(workspace.id)}

        response = await async_client.post(
            "/api/v1/datasets", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=dataset_json
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 0

    async def test_create_dataset_with_existent_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(name="name")
        dataset_json = {"name": "name", "workspace_id": str(dataset.workspace_id)}

        response = await async_client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

        assert response.status_code == 409
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 1

    async def test_create_dataset_with_nonexistent_workspace_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset_json = {"name": "name", "workspace_id": str(uuid4())}

        response = await async_client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 0

    @pytest.mark.parametrize(
        ("settings", "expected_settings"),
        [
            ({"type": "text"}, {"type": "text", "use_markdown": False}),
            ({"type": "text", "discarded": "value"}, {"type": "text", "use_markdown": False}),
            ({"type": "text", "use_markdown": False}, {"type": "text", "use_markdown": False}),
        ],
    )
    async def test_create_dataset_field(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        settings: dict,
        expected_settings: dict,
    ):
        dataset = await DatasetFactory.create()
        field_json = {"name": "name", "title": "title", "settings": settings}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 1

        response_body = response.json()
        assert await db.get(Field, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "name": "name",
            "title": "title",
            "required": False,
            "settings": expected_settings,
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    async def test_create_dataset_field_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(f"/api/v1/datasets/{dataset.id}/fields", json=field_json)

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=field_json,
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 1

    async def test_create_dataset_field_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json=field_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    @pytest.mark.parametrize("invalid_name", ["", " ", "  ", "-", "--", "_", "__", "A", "AA", "invalid_nAmE"])
    async def test_create_dataset_field_with_invalid_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, invalid_name: str
    ):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": invalid_name,
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_invalid_max_length_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "a" * (FIELD_CREATE_NAME_MAX_LENGTH + 1),
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        # assert db.query(Field).count() == 0
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_invalid_max_length_title(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "a" * (FIELD_CREATE_TITLE_MAX_LENGTH + 1),
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "settings",
        [
            {},
            None,
            {"type": "wrong-type"},
            {"type": "text", "use_markdown": None},
            {"type": "rating", "options": None},
            {"type": "rating", "options": []},
        ],
    )
    async def test_create_dataset_field_with_invalid_settings(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, settings: dict
    ):
        dataset = await DatasetFactory.create()
        field_json = {
            "name": "name",
            "title": "Title",
            "settings": settings,
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_existent_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        field = await FieldFactory.create(name="name")
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{field.dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 409
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 1

    async def test_create_dataset_field_with_published_dataset(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        field_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Field cannot be created for a published dataset"}
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_field_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        await DatasetFactory.create()
        field_json = {
            "name": "text",
            "title": "Text",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{uuid4()}/fields", headers=owner_auth_header, json=field_json
        )

        assert response.status_code == 404
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    @pytest.mark.parametrize(
        ("settings", "expected_settings"),
        [
            ({"type": "text"}, {"type": "text", "use_markdown": False}),
            ({"type": "text", "use_markdown": True}, {"type": "text", "use_markdown": True}),
            ({"type": "text", "use_markdown": False}, {"type": "text", "use_markdown": False}),
            (
                {
                    "type": "rating",
                    "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                },
                {
                    "type": "rating",
                    "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                },
            ),
            (
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive", "description": "Texts with positive sentiment"},
                        {"value": "negative", "text": "Negative", "description": "Texts with negative sentiment"},
                        {"value": "neutral", "text": "Neutral", "description": "Texts with neutral sentiment"},
                    ],
                    "visible_options": 10,
                },
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive", "description": "Texts with positive sentiment"},
                        {"value": "negative", "text": "Negative", "description": "Texts with negative sentiment"},
                        {"value": "neutral", "text": "Neutral", "description": "Texts with neutral sentiment"},
                    ],
                    "visible_options": 10,
                },
            ),
            (
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive"},
                        {"value": "negative", "text": "Negative"},
                        {"value": "neutral", "text": "Neutral"},
                    ],
                },
                {
                    "type": "label_selection",
                    "options": [
                        {"value": "positive", "text": "Positive", "description": None},
                        {"value": "negative", "text": "Negative", "description": None},
                        {"value": "neutral", "text": "Neutral", "description": None},
                    ],
                    "visible_options": None,
                },
            ),
            (
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": "Completion A is the best"},
                        {"value": "completion-b", "text": "Completion B", "description": "Completion B is the best"},
                        {"value": "completion-c", "text": "Completion C", "description": "Completion C is the best"},
                        {"value": "completion-d", "text": "Completion D", "description": "Completion D is the best"},
                    ],
                },
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": "Completion A is the best"},
                        {"value": "completion-b", "text": "Completion B", "description": "Completion B is the best"},
                        {"value": "completion-c", "text": "Completion C", "description": "Completion C is the best"},
                        {"value": "completion-d", "text": "Completion D", "description": "Completion D is the best"},
                    ],
                },
            ),
            (
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": None},
                        {"value": "completion-b", "text": "Completion b", "description": None},
                        {"value": "completion-c", "text": "Completion C", "description": None},
                        {"value": "completion-d", "text": "Completion D", "description": None},
                    ],
                },
                {
                    "type": "ranking",
                    "options": [
                        {"value": "completion-a", "text": "Completion A", "description": None},
                        {"value": "completion-b", "text": "Completion b", "description": None},
                        {"value": "completion-c", "text": "Completion C", "description": None},
                        {"value": "completion-d", "text": "Completion D", "description": None},
                    ],
                },
            ),
        ],
    )
    async def test_create_dataset_question(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        settings: dict,
        expected_settings: dict,
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "settings": settings,
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

        response_body = response.json()
        assert await db.get(Question, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "name": "name",
            "title": "title",
            "description": None,
            "required": False,
            "settings": expected_settings,
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    async def test_create_dataset_question_with_description(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "description": "description",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

        response_body = response.json()
        assert await db.get(Question, UUID(response_body["id"]))
        assert response_body["description"] == "description"

    async def test_create_dataset_question_without_authentication(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(f"/api/v1/datasets/{dataset.id}/questions", json=question_json)

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=question_json,
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

    async def test_create_dataset_question_as_admin_for_different_workspace(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])

        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=question_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json=question_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    @pytest.mark.parametrize("invalid_name", ["", " ", "  ", "-", "--", "_", "__", "A", "AA", "invalid_nAmE"])
    async def test_create_dataset_question_with_invalid_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, invalid_name: str
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": invalid_name,
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_invalid_max_length_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "a" * (QUESTION_CREATE_NAME_MAX_LENGTH + 1),
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_invalid_max_length_title(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "a" * (QUESTION_CREATE_TITLE_MAX_LENGTH + 1),
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_invalid_max_length_description(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_json = {
            "name": "name",
            "title": "title",
            "description": "a" * (QUESTION_CREATE_DESCRIPTION_MAX_LENGTH + 1),
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_existent_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        question = await QuestionFactory.create(name="name")
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{question.dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 409
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 1

    async def test_create_dataset_question_with_published_dataset(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        question_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Question cannot be created for a published dataset"}
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_question_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        await DatasetFactory.create()
        question_json = {
            "name": "text",
            "title": "Text",
            "settings": {"type": "text"},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{uuid4()}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 404
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "settings",
        [
            None,
            {},
            {"type": "wrong"},
            {"type": "text", "use_markdown": None},
            {"type": "text", "use_markdown": "wrong"},
            {
                "type": "rating",
                "options": [
                    {"value": "A wrong value"},
                    {"value": "B wrong value"},
                    {"value": "C wrong value"},
                    {"value": "D wrong value"},
                ],
            },
            {"type": "rating", "options": [{"value": value} for value in range(0, RATING_OPTIONS_MIN_ITEMS - 1)]},
            {"type": "rating", "options": [{"value": value} for value in range(0, RATING_OPTIONS_MAX_ITEMS + 1)]},
            {"type": "rating", "options": "invalid"},
            {"type": "rating", "options": [{"value": 1}, {"value": 1}]},
            {"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": 13}]},
            {"type": "rating", "options": [{"value": 1}, {"value": 2}, {"value": -13}]},
            {"type": "label_selection", "options": []},
            {"type": "label_selection", "options": [{"value": "just_one_label", "text": "Just one label"}]},
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": 0,
            },
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
                "visible_options": -1,
            },
            {
                "type": "label_selection",
                "options": [{"value": "", "text": "a"}, {"value": "b", "text": "b"}],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "".join(["a" for _ in range(VALUE_TEXT_OPTION_VALUE_MAX_LENGTH + 1)]), "text": "a"},
                    {"value": "b", "text": "b"},
                ],
            },
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": ""}, {"value": "b", "text": "b"}],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "a", "text": "".join(["a" for _ in range(VALUE_TEXT_OPTION_TEXT_MAX_LENGTH + 1)])},
                    {"value": "b", "text": "b"},
                ],
            },
            {
                "type": "label_selection",
                "options": [{"value": "a", "text": "a", "description": ""}, {"value": "b", "text": "b"}],
            },
            {
                "type": "label_selection",
                "options": [
                    {
                        "value": "a",
                        "text": "a",
                        "description": "".join(["a" for _ in range(VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH + 1)]),
                    },
                    {"value": "b", "text": "b"},
                ],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {
                        "value": "a",
                        "text": "a",
                        "description": "".join(["a" for _ in range(VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH + 1)]),
                    },
                    {"value": "b", "text": "b", "description": "b"},
                ],
            },
        ],
    )
    async def test_create_dataset_question_with_invalid_settings(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        settings: dict,
    ):
        dataset = await DatasetFactory.create()
        question_json = {"name": "question", "title": "Question", "settings": settings}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_records(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        test_telemetry: MagicMock,
        db: "AsyncSession",
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)

        question_a = await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        question_b = await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "external_id": "1",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "submitted",
                            "user_id": str(owner.id),
                        }
                    ],
                    "suggestions": [
                        {
                            "question_id": str(question_a.id),
                            "type": "model",
                            "score": 0.8,
                            "value": "yes",
                            "agent": "unit-test-agent",
                        },
                        {
                            "question_id": str(question_b.id),
                            "value": "yes",
                        },
                    ],
                },
                {
                    "fields": {"input": "Say Hello", "output": "Hi"},
                    "suggestions": [{"question_id": str(question_a.id), "value": "no"}],
                },
                {
                    "fields": {"input": "Say Pello", "output": "Hello World"},
                    "external_id": "3",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                            "status": "submitted",
                            "user_id": str(owner.id),
                        }
                    ],
                },
                {
                    "fields": {"input": "Say Hello", "output": "Good Morning"},
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "no"}},
                            "status": "discarded",
                            "user_id": str(owner.id),
                        }
                    ],
                },
                {
                    "fields": {"input": "Say Hello", "output": "Say Hello"},
                    "responses": [
                        {
                            "user_id": str(owner.id),
                            "status": "discarded",
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 204, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 5
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 4
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 3

        records = (await db.execute(select(Record))).scalars().all()
        mock_search_engine.add_records.assert_called_once_with(dataset, records)

        test_telemetry.assert_called_once_with(
            action="DatasetRecordsCreated", data={"records": len(records_json["items"])}
        )

    async def test_create_dataset_records_with_response_for_multiple_users(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        db: "AsyncSession",
        owner: "User",
        owner_auth_header: dict,
    ):
        workspace = await WorkspaceFactory.create()

        dataset = await DatasetFactory.create(status=DatasetStatus.ready, workspace=workspace)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)
        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        annotator = await AnnotatorFactory.create(workspaces=[workspace])

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "external_id": "1",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "submitted",
                            "user_id": str(owner.id),
                        },
                        {
                            "status": "discarded",
                            "user_id": str(annotator.id),
                        },
                    ],
                },
                {
                    "fields": {"input": "Say Pello", "output": "Hello World"},
                    "external_id": "3",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                            "status": "submitted",
                            "user_id": str(annotator.id),
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        await db.refresh(annotator)
        await db.refresh(owner)

        assert response.status_code == 204, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 2
        assert (await db.execute(select(func.count(Response.id)).where(Response.user_id == annotator.id))).scalar() == 2
        assert (await db.execute(select(func.count(Response.id)).where(Response.user_id == owner.id))).scalar() == 1

        records = (await db.execute(select(Record))).scalars().all()
        mock_search_engine.add_records.assert_called_once_with(dataset, records)

    async def test_create_dataset_records_with_response_for_unknown_user(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)
        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "external_id": "1",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "submitted",
                            "user_id": str(uuid4()),
                        },
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_dataset_records_with_duplicated_response_for_an_user(
        self, async_client: "AsyncClient", db: "AsyncSession", owner: "User", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)
        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "external_id": "1",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "submitted",
                            "user_id": str(owner.id),
                        },
                        {
                            "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                            "status": "submitted",
                            "user_id": str(owner.id),
                        },
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "model": "Request",
                    "errors": [
                        {
                            "loc": ["body", "items", 0, "responses"],
                            "msg": f"Responses contains several responses for the same user_id: {str(owner.id)!r}",
                            "type": "value_error",
                        }
                    ],
                },
            }
        }
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"question_id": str(uuid4()), "value": "yes"},
            {"value": {"this": "is not a valid response for a TextQuestion"}},
        ],
    )
    async def test_create_dataset_records_with_not_valid_suggestion(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, payload: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        question = await TextFieldFactory.create(name="input", dataset=dataset)

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={"question_id": str(question.id), **payload},
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 0

    async def test_create_dataset_records_with_missing_required_fields(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await FieldFactory.create(name="input", dataset=dataset, required=True)
        await FieldFactory.create(name="output", dataset=dataset, required=True)

        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello"},
                },
                {
                    "fields": {"input": "Say Hello", "output": "Hi"},
                },
                {
                    "fields": {"input": "Say Pello", "output": "Hello World"},
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Missing required value for field: 'output'"}
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_create_dataset_records_with_wrong_value_field(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await FieldFactory.create(name="input", dataset=dataset)
        await FieldFactory.create(name="output", dataset=dataset)

        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": 33},
                },
                {
                    "fields": {"input": "Say Hello", "output": "Hi"},
                },
                {
                    "fields": {"input": "Say Pello", "output": "Hello World"},
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Wrong value found for field 'output'. Expected 'str', found 'int'"}
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_create_dataset_records_with_extra_fields(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await FieldFactory.create(name="input", dataset=dataset)

        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "unexpected"},
                },
                {
                    "fields": {"input": "Say Hello"},
                },
                {
                    "fields": {"input": "Say Pello"},
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Error: found fields values for non configured fields: ['output']"}
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_create_dataset_records_with_index_error(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        records_json = {
            "items": [
                {"fields": {"input": "Say Hello", "output": "Hello"}},
                {"fields": {"input": "Say Hello", "output": "Hi"}},
                {"fields": {"input": "Say Pello", "output": "Hello World"}},
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

        assert not mock_search_engine.create_index.called

    async def test_create_dataset_records_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "ouput": "Hello"},
                    "external_id": "1",
                    "response": {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                    },
                },
            ],
        }

        response = await async_client.post(f"/api/v1/datasets/{dataset.id}/records", json=records_json)

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_dataset_records_as_admin(
        self,
        async_client: "AsyncClient",
        mock_search_engine: "SearchEngine",
        db: "AsyncSession",
        test_telemetry: MagicMock,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        admin = await AdminFactory.create(workspaces=[dataset.workspace])

        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)

        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "external_id": "1",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "submitted",
                            "user_id": str(admin.id),
                        }
                    ],
                },
                {
                    "fields": {"input": "Say Hello", "output": "Hi"},
                },
                {
                    "fields": {"input": "Say Pello", "output": "Hello World"},
                    "external_id": "3",
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                            "status": "submitted",
                            "user_id": str(admin.id),
                        }
                    ],
                },
                {
                    "fields": {"input": "Say Hello", "output": "Good Morning"},
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "no"}},
                            "status": "discarded",
                            "user_id": str(admin.id),
                        }
                    ],
                },
                {
                    "fields": {"input": "Say Hello", "output": "Say Hello"},
                    "responses": [
                        {
                            "user_id": str(admin.id),
                            "status": "discarded",
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: admin.api_key}, json=records_json
        )

        assert response.status_code == 204, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 5
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 4

        records = (await db.execute(select(Record))).scalars().all()
        mock_search_engine.add_records.assert_called_once_with(dataset, records)

        test_telemetry.assert_called_once_with(
            action="DatasetRecordsCreated", data={"records": len(records_json["items"])}
        )

    async def test_create_dataset_records_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "ouput": "Hello"},
                    "external_id": "1",
                    "response": {
                        "values": {
                            "input_ok": {"value": "yes"},
                            "output_ok": {"value": "yes"},
                        },
                        "status": "submitted",
                    },
                },
            ],
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json=records_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_dataset_records_with_submitted_response(
        self, async_client: "AsyncClient", db: "AsyncSession", owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)

        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "submitted",
                            "user_id": str(owner.id),
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 204
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 1
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

    async def test_create_dataset_records_with_submitted_response_without_values(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "ouput": "Hello"},
                    "responses": [
                        {
                            "user_id": str(owner.id),
                            "status": "submitted",
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_create_dataset_records_with_discarded_response(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)

        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "discarded",
                            "user_id": str(owner.id),
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 204
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 1
        assert (
            await db.execute(select(func.count(Response.id)).filter(Response.status == ResponseStatus.discarded))
        ).scalar() == 1

    async def test_create_dataset_records_with_invalid_response_status(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "ouput": "Hello"},
                    "responses": [
                        {
                            "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                            "status": "invalid",
                            "user_id": str(owner.id),
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_create_dataset_records_with_discarded_response_without_values(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)

        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
                    "responses": [
                        {
                            "status": "discarded",
                            "user_id": str(owner.id),
                        }
                    ],
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 204
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 1

    async def test_create_dataset_records_with_non_published_dataset(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.draft)
        records_json = {
            "items": [
                {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": "1"},
            ],
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Records cannot be created for a non published dataset"}
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_dataset_records_with_less_items_than_allowed(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "ouput": "Hello"},
                    "external_id": str(external_id),
                }
                for external_id in range(0, RECORDS_CREATE_MIN_ITEMS - 1)
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_dataset_records_with_more_items_than_allowed(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "ouput": "Hello"},
                    "external_id": str(external_id),
                }
                for external_id in range(0, RECORDS_CREATE_MAX_ITEMS + 1)
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_dataset_records_with_invalid_records(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 1},
                {"fields": "invalid", "external_id": 2},
                {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 3},
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_create_dataset_records_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        await DatasetFactory.create()
        records_json = {
            "items": [
                {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 1},
                {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 2},
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{uuid4()}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 404
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_dataset_records(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine, role: UserRole
    ):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)
        records = await RecordFactory.create_batch(10, dataset=dataset)
        random_uuids = [str(uuid4()) for _ in range(0, 5)]

        records_ids = [str(record.id) for record in records]

        uuids_str = ",".join(records_ids + random_uuids)

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: user.api_key},
            params={"ids": uuids_str},
        )

        assert response.status_code == 204, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        # `delete_records` is called with the records returned by the delete statement, which are different ORM objects
        # than the ones created by the factory
        mock_search_engine.delete_records.assert_called_once_with(dataset=dataset, records=ANY)

    async def test_delete_dataset_records_with_no_ids(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            params={"ids": ""},
        )

        assert response.status_code == 422

    async def test_delete_dataset_records_exceeding_limit(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        records = await RecordFactory.create_batch(200, dataset=dataset)

        records_ids = [str(record.id) for record in records]

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            params={"ids": ",".join(records_ids)},
        )

        assert response.status_code == 422

    async def test_delete_dataset_records_from_another_dataset(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset_a = await DatasetFactory.create()
        dataset_b = await DatasetFactory.create()
        records_a = await RecordFactory.create_batch(10, dataset=dataset_a)
        records_b = await RecordFactory.create_batch(10, dataset=dataset_b)

        records_ids_a = [str(record.id) for record in records_a]
        records_ids_b = [str(record.id) for record in records_b]

        uuids_str = ",".join(records_ids_a + records_ids_b)

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset_a.id}/records", headers=owner_auth_header, params={"ids": uuids_str}
        )

        assert response.status_code == 204

    async def test_delete_dataset_records_as_admin_from_another_workspace(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(role=UserRole.admin)

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: user.api_key},
            params={"ids": ""},
        )

        assert response.status_code == 403

    async def test_delete_dataset_records_as_annotator(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=UserRole.annotator)

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: user.api_key},
            params={"ids": ""},
        )

        assert response.status_code == 403

    async def test_search_dataset_records(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search", headers=owner_auth_header, json=query_json
        )

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=Query(
                text=TextQuery(
                    q="Hello",
                    field="input",
                )
            ),
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
        )
        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "record": {
                        "id": str(records[0].id),
                        "fields": {"input": "input_a", "output": "output_a"},
                        "metadata": None,
                        "external_id": records[0].external_id,
                        "inserted_at": records[0].inserted_at.isoformat(),
                        "updated_at": records[0].updated_at.isoformat(),
                    },
                    "query_score": 14.2,
                },
                {
                    "record": {
                        "id": str(records[1].id),
                        "fields": {"input": "input_b", "output": "output_b"},
                        "metadata": {"unit": "test"},
                        "external_id": records[1].external_id,
                        "inserted_at": records[1].inserted_at.isoformat(),
                        "updated_at": records[1].updated_at.isoformat(),
                    },
                    "query_score": 12.2,
                },
            ],
            "total": 2,
        }

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin, UserRole.owner])
    @pytest.mark.parametrize(
        "includes",
        [[RecordInclude.responses], [RecordInclude.suggestions], [RecordInclude.responses, RecordInclude.suggestions]],
    )
    async def test_search_dataset_records_with_include(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        role: UserRole,
        includes: List[RecordInclude],
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)
        dataset, questions, records, responses, suggestions = await self.create_dataset_with_user_responses(
            user, workspace
        )
        response_a_user, response_b_user = responses[1], responses[3]
        suggestion_a, suggestion_b = suggestions

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
        params = [("include", include.value) for include in includes]
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json=query_json,
            params=params,
        )

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=Query(
                text=TextQuery(
                    q="Hello",
                    field="input",
                )
            ),
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
        )

        expected = {
            "items": [
                {
                    "record": {
                        "id": str(records[0].id),
                        "fields": {
                            "input": "input_a",
                            "output": "output_a",
                        },
                        "metadata": None,
                        "external_id": records[0].external_id,
                        "inserted_at": records[0].inserted_at.isoformat(),
                        "updated_at": records[0].updated_at.isoformat(),
                    },
                    "query_score": 14.2,
                },
                {
                    "record": {
                        "id": str(records[1].id),
                        "fields": {
                            "input": "input_b",
                            "output": "output_b",
                        },
                        "metadata": {"unit": "test"},
                        "external_id": records[1].external_id,
                        "inserted_at": records[1].inserted_at.isoformat(),
                        "updated_at": records[1].updated_at.isoformat(),
                    },
                    "query_score": 12.2,
                },
            ],
            "total": 2,
        }

        if RecordInclude.responses in includes:
            expected["items"][0]["record"]["responses"] = [
                {
                    "id": str(response_a_user.id),
                    "values": None,
                    "status": "discarded",
                    "user_id": str(response_a_user.user_id),
                    "inserted_at": response_a_user.inserted_at.isoformat(),
                    "updated_at": response_a_user.updated_at.isoformat(),
                }
            ]
            expected["items"][1]["record"]["responses"] = [
                {
                    "id": str(response_b_user.id),
                    "values": {
                        "input_ok": {"value": "no"},
                        "output_ok": {"value": "no"},
                    },
                    "status": "submitted",
                    "user_id": str(response_b_user.user_id),
                    "inserted_at": response_b_user.inserted_at.isoformat(),
                    "updated_at": response_b_user.updated_at.isoformat(),
                }
            ]

        if RecordInclude.suggestions in includes:
            expected["items"][0]["record"]["suggestions"] = [
                {
                    "id": str(suggestion_a.id),
                    "value": "option-1",
                    "score": None,
                    "agent": None,
                    "type": None,
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][1]["record"]["suggestions"] = [
                {
                    "id": str(suggestion_b.id),
                    "value": "option-2",
                    "score": 0.75,
                    "agent": "unit-test-agent",
                    "type": "model",
                    "question_id": str(questions[0].id),
                }
            ]

        assert response.status_code == 200
        assert response.json() == expected

    async def test_search_dataset_records_with_response_status_filter(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, _, _, _ = await self.create_dataset_with_user_responses(owner, workspace)
        mock_search_engine.search.return_value = SearchResponses(items=[])

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"response_status": ResponseStatus.submitted.value},
        )

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=Query(text=TextQuery(q="Hello", field="input")),
            user_response_status_filter=UserResponseStatusFilter(user=owner, statuses=[ResponseStatusFilter.submitted]),
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
        )
        assert response.status_code == 200

    async def test_search_dataset_records_with_offset_and_limit(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"offset": 0, "limit": 5},
        )

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=Query(text=TextQuery(q="Hello", field="input")),
            user_response_status_filter=None,
            offset=0,
            limit=5,
        )
        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json["items"]) == 2
        assert response_json["total"] == 2

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_search_dataset_records_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        workspace_a = await WorkspaceFactory.create()
        workspace_b = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace_a], role=role)
        dataset, _, _, _, _ = await self.create_dataset_with_user_responses(user, workspace_b)

        query_json = {"query": {"text": {"q": "unit test", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json=query_json,
        )

        assert response.status_code == 403

    async def test_search_dataset_records_with_non_existent_field(
        self, async_client: "AsyncClient", owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, _, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        query_json = {"query": {"text": {"q": "unit test", "field": "i do not exist"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search", headers=owner_auth_header, json=query_json
        )

        assert response.status_code == 422

    async def test_search_dataset_with_non_existent_dataset(self, async_client: "AsyncClient", owner_auth_header):
        query_json = {"query": {"text": {"q": "unit test", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{uuid4()}/records/search", headers=owner_auth_header, json=query_json
        )

        assert response.status_code == 404

    async def test_publish_dataset(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: SearchEngine,
        test_telemetry: MagicMock,
        owner_auth_header,
    ) -> None:
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await RatingQuestionFactory.create(dataset=dataset, required=True)

        response = await async_client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

        assert response.status_code == 200
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

        response_body = response.json()
        assert response_body["status"] == "ready"

        test_telemetry.assert_called_once_with(action="PublishedDataset", data={"questions": ["rating"]})
        mock_search_engine.create_index.assert_called_once_with(dataset)

    async def test_publish_dataset_with_error_on_index_creation(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        mock_search_engine.create_index.side_effect = ValueError("Error creating index")

        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await QuestionFactory.create(settings={"type": "invalid"}, dataset=dataset, required=True)

        response = await async_client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_publish_dataset_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create()
        await QuestionFactory.create(dataset=dataset)

        response = await async_client.put(f"/api/v1/datasets/{dataset.id}/publish")

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_publish_dataset_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await RatingQuestionFactory.create(dataset=dataset, required=True)
        admin = await AdminFactory.create(workspaces=[dataset.workspace])

        response = await async_client.put(
            f"/api/v1/datasets/{dataset.id}/publish", headers={API_KEY_HEADER_NAME: admin.api_key}
        )

        assert response.status_code == 200
        assert (await db.get(Dataset, dataset.id)).status == DatasetStatus.ready

        response_body = response.json()
        assert response_body["status"] == "ready"

    async def test_publish_dataset_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create()
        await QuestionFactory.create(dataset=dataset, required=True)
        annotator = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        response = await async_client.put(
            f"/api/v1/datasets/{dataset.id}/publish", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_publish_dataset_already_published(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await QuestionFactory.create(dataset=dataset)

        response = await async_client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

        assert response.status_code == 422
        assert response.json() == {"detail": "Dataset is already published"}
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_publish_dataset_without_fields(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=False)
        await TextQuestionFactory.create(dataset=dataset, required=True)

        response = await async_client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

        assert response.status_code == 422
        assert response.json() == {"detail": "Dataset cannot be published without required fields"}
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_publish_dataset_without_questions(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, required=True)
        await TextQuestionFactory.create(dataset=dataset, required=False)

        response = await async_client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

        assert response.status_code == 422
        assert response.json() == {"detail": "Dataset cannot be published without required questions"}
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    async def test_publish_dataset_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await QuestionFactory.create(dataset=dataset)

        response = await async_client.put(f"/api/v1/datasets/{uuid4()}/publish", headers=owner_auth_header)

        assert response.status_code == 404
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "payload",
        [
            {"name": "New Name", "guidelines": "New Guidelines"},
            {"name": "New Name"},
            {"guidelines": "New Guidelines"},
            {},
            {"status": DatasetStatus.draft, "workspace_id": str(uuid4())},
        ],
    )
    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
    async def test_update_dataset(self, async_client: "AsyncClient", db: "AsyncSession", role: UserRole, payload: dict):
        dataset = await DatasetFactory.create(
            name="Current Name", guidelines="Current Guidelines", status=DatasetStatus.ready
        )
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json=payload,
        )

        name = payload.get("name") or dataset.name
        if "guidelines" in payload:
            guidelines = payload["guidelines"]
        else:
            guidelines = dataset.guidelines

        assert response.status_code == 200
        assert response.json() == {
            "id": str(dataset.id),
            "name": name,
            "guidelines": guidelines,
            "status": "ready",
            "workspace_id": str(dataset.workspace_id),
            "inserted_at": dataset.inserted_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
        }

        dataset = await db.get(Dataset, dataset.id)
        assert dataset.name == name
        assert dataset.guidelines == guidelines

    @pytest.mark.parametrize(
        "dataset_json",
        [
            {"name": None},
            {"name": ""},
            {"name": "123$abc"},
            {"name": "unit@test"},
            {"name": "-test-dataset"},
            {"name": "_test-dataset"},
            {"name": "a" * (DATASET_NAME_MAX_LENGTH + 1)},
            {"name": "test-dataset", "guidelines": ""},
            {"name": "test-dataset", "guidelines": "a" * (DATASET_GUIDELINES_MAX_LENGTH + 1)},
        ],
    )
    @pytest.mark.asyncio
    async def test_update_dataset_with_invalid_settings(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, dataset_json: dict
    ):
        dataset = await DatasetFactory.create(
            name="Current Name", guidelines="Current Guidelines", status=DatasetStatus.ready
        )

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header, json=dataset_json
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_dataset_with_invalid_payload(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}",
            headers=owner_auth_header,
            json={"name": {"this": {"is": "invalid"}}, "guidelines": {"this": {"is": "invalid"}}},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_dataset_non_existent(self, async_client: "AsyncClient", owner_auth_header: dict):
        response = await async_client.patch(
            f"/api/v1/datasets/{uuid4()}",
            headers=owner_auth_header,
            json={"name": "New Name", "guidelines": "New Guidelines"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_dataset_as_admin_from_different_workspace(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(role=UserRole.admin)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"name": "New Name", "guidelines": "New Guidelines"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_dataset_as_annotator(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(role=UserRole.annotator, workspaces=[dataset.workspace])

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"name": "New Name", "guidelines": "New Guidelines"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_dataset_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}",
            json={"name": "New Name", "guidelines": "New Guidelines"},
        )

        assert response.status_code == 401

    async def test_delete_dataset(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset)
        await TextQuestionFactory.create(dataset=dataset)

        other_dataset = await DatasetFactory.create()
        other_field = await TextFieldFactory.create(dataset=other_dataset)
        other_question = await TextQuestionFactory.create(dataset=other_dataset)
        other_record = await RecordFactory.create(dataset=other_dataset)
        other_response = await ResponseFactory.create(record=other_record, user=owner)

        response = await async_client.delete(f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header)

        assert response.status_code == 200

        # assert [dataset.id for dataset in (await db.execute(select(Dataset))).all()] == [other_dataset.id]
        # assert [field.id for field in db.query(Field).all()] == [other_field.id]
        # assert [question.id for question in db.query(Question).all()] == [other_question.id]
        # assert [record.id for record in db.query(Record).all()] == [other_record.id]
        # assert [response.id for response in db.query(Response).all()] == [other_response.id]
        # assert [workspace.id for workspace in db.query(Workspace).order_by(Workspace.inserted_at.asc()).all()] == [
        #     dataset.workspace_id,
        #     other_dataset.workspace_id,
        # ]

        mock_search_engine.delete_index.assert_called_once_with(dataset)

    async def test_delete_published_dataset(
        self, async_client: "AsyncClient", db: "AsyncSession", owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset)
        await TextQuestionFactory.create(dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create(record=record, user=owner)

        other_dataset = await DatasetFactory.create()
        other_field = await TextFieldFactory.create(dataset=other_dataset)
        other_question = await TextQuestionFactory.create(dataset=other_dataset)
        other_record = await RecordFactory.create(dataset=other_dataset)
        other_response = await ResponseFactory.create(record=other_record, user=owner)

        response = await async_client.delete(f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header)

        assert response.status_code == 200
        # assert [dataset.id for dataset in db.query(Dataset).all()] == [other_dataset.id]
        # assert [field.id for field in db.query(Field).all()] == [other_field.id]
        # assert [question.id for question in db.query(Question).all()] == [other_question.id]
        # assert [record.id for record in db.query(Record).all()] == [other_record.id]
        # assert [response.id for response in db.query(Response).all()] == [other_response.id]
        # assert [workspace.id for workspace in db.query(Workspace).order_by(Workspace.inserted_at.asc()).all()] == [
        #     dataset.workspace_id,
        #     other_dataset.workspace_id,
        # ]

    async def test_delete_dataset_without_authentication(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.delete(f"/api/v1/datasets/{dataset.id}")

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 1

        assert not mock_search_engine.delete_index.called

    async def test_delete_dataset_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create()
        admin = await AdminFactory.create(workspaces=[dataset.workspace])

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: admin.api_key}
        )

        assert response.status_code == 200
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 0

    async def test_delete_dataset_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create()

        response = await async_client.delete(
            f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 1

    async def test_delete_dataset_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        await DatasetFactory.create()

        response = await async_client.delete(f"/api/v1/datasets/{uuid4()}", headers=owner_auth_header)

        assert response.status_code == 404
        assert (await db.execute(select(func.count(Dataset.id)))).scalar() == 1
