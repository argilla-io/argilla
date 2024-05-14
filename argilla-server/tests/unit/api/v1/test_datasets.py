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
import math
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type, Union
from unittest.mock import ANY, MagicMock
from uuid import UUID, uuid4

import pytest
from argilla_server.apis.v1.handlers.datasets.records import LIST_DATASET_RECORDS_LIMIT_DEFAULT
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import (
    DatasetStatus,
    OptionsOrder,
    RecordInclude,
    ResponseStatusFilter,
    SimilarityOrder,
)
from argilla_server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    Record,
    Response,
    ResponseStatus,
    Suggestion,
    User,
    UserRole,
    Vector,
    VectorSettings,
)
from argilla_server.schemas.v1.datasets import (
    DATASET_GUIDELINES_MAX_LENGTH,
    DATASET_NAME_MAX_LENGTH,
)
from argilla_server.schemas.v1.fields import FIELD_CREATE_NAME_MAX_LENGTH, FIELD_CREATE_TITLE_MAX_LENGTH
from argilla_server.schemas.v1.metadata_properties import (
    METADATA_PROPERTY_CREATE_NAME_MAX_LENGTH,
    METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH,
    TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS,
)
from argilla_server.schemas.v1.records import RECORDS_CREATE_MAX_ITEMS, RECORDS_CREATE_MIN_ITEMS
from argilla_server.schemas.v1.vector_settings import (
    VECTOR_SETTINGS_CREATE_NAME_MAX_LENGTH,
    VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH,
)
from argilla_server.search_engine import (
    FloatMetadataFilter,
    IntegerMetadataFilter,
    MetadataFilter,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    SortBy,
    TermsMetadataFilter,
    TextQuery,
    UserResponseStatusFilter,
)
from sqlalchemy import func, inspect, select

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    FieldFactory,
    FloatMetadataPropertyFactory,
    IntegerMetadataPropertyFactory,
    LabelSelectionQuestionFactory,
    MetadataPropertyFactory,
    MultiLabelSelectionQuestionFactory,
    OwnerFactory,
    QuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    SuggestionFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
    VectorFactory,
    VectorSettingsFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestSuiteDatasets:
    async def test_list_current_user_datasets(self, async_client: "AsyncClient", owner_auth_header: dict) -> None:
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
                    "allow_extra_metadata": True,
                    "status": "draft",
                    "workspace_id": str(dataset_a.workspace_id),
                    "last_activity_at": dataset_a.last_activity_at.isoformat(),
                    "inserted_at": dataset_a.inserted_at.isoformat(),
                    "updated_at": dataset_a.updated_at.isoformat(),
                },
                {
                    "id": str(dataset_b.id),
                    "name": "dataset-b",
                    "guidelines": "guidelines",
                    "allow_extra_metadata": True,
                    "status": "draft",
                    "workspace_id": str(dataset_b.workspace_id),
                    "last_activity_at": dataset_b.last_activity_at.isoformat(),
                    "inserted_at": dataset_b.inserted_at.isoformat(),
                    "updated_at": dataset_b.updated_at.isoformat(),
                },
                {
                    "id": str(dataset_c.id),
                    "name": "dataset-c",
                    "guidelines": None,
                    "allow_extra_metadata": True,
                    "status": "ready",
                    "workspace_id": str(dataset_c.workspace_id),
                    "last_activity_at": dataset_c.last_activity_at.isoformat(),
                    "inserted_at": dataset_c.inserted_at.isoformat(),
                    "updated_at": dataset_c.updated_at.isoformat(),
                },
            ]
        }

    async def test_list_current_user_datasets_without_authentication(self, async_client: "AsyncClient") -> None:
        response = await async_client.get("/api/v1/me/datasets")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_current_user_datasets_as_restricted_user_role(
        self, async_client: "AsyncClient", role: UserRole
    ) -> None:
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        await DatasetFactory.create(name="dataset-a", workspace=workspace)
        await DatasetFactory.create(name="dataset-b", workspace=workspace)
        await DatasetFactory.create(name="dataset-c")

        response = await async_client.get("/api/v1/me/datasets", headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 200

        response_body = response.json()
        assert [dataset["name"] for dataset in response_body["items"]] == ["dataset-a", "dataset-b"]

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.annotator, UserRole.admin])
    async def test_list_current_user_datasets_by_workspace_id(
        self, async_client: "AsyncClient", role: UserRole
    ) -> None:
        workspace = await WorkspaceFactory.create()
        another_workspace = await WorkspaceFactory.create()

        user = (
            await UserFactory.create(role=role)
            if role == UserRole.owner
            else await UserFactory.create(workspaces=[workspace], role=role)
        )

        await DatasetFactory.create(name="dataset-a", workspace=workspace)
        await DatasetFactory.create(name="dataset-b", workspace=another_workspace)

        response = await async_client.get(
            "/api/v1/me/datasets", params={"workspace_id": workspace.id}, headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [dataset["name"] for dataset in response_body["items"]] == ["dataset-a"]

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
                    "dataset_id": str(dataset.id),
                    "inserted_at": text_field_a.inserted_at.isoformat(),
                    "updated_at": text_field_a.updated_at.isoformat(),
                },
                {
                    "id": str(text_field_b.id),
                    "name": "text-field-b",
                    "title": "Text Field B",
                    "required": False,
                    "settings": {"type": "text", "use_markdown": False},
                    "dataset_id": str(dataset.id),
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
                    "dataset_id": str(text_question.dataset_id),
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
                    "dataset_id": str(rating_question.dataset_id),
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
                    "options_order": OptionsOrder.natural,
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
                    "dataset_id": str(question.dataset_id),
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

    async def test_list_current_user_dataset_metadata_properties(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        terms_property = await TermsMetadataPropertyFactory.create(name="terms", dataset=dataset)
        integer_property = await IntegerMetadataPropertyFactory.create(name="integer", dataset=dataset)
        float_property = await FloatMetadataPropertyFactory.create(name="float", dataset=dataset)

        await TermsMetadataPropertyFactory.create()
        await IntegerMetadataPropertyFactory.create()
        await FloatMetadataPropertyFactory.create()

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header
        )

        assert response.status_code == 200, response.json()
        assert response.json() == {
            "items": [
                {
                    "id": str(terms_property.id),
                    "name": "terms",
                    "title": terms_property.title,
                    "settings": {"type": "terms", "values": ["a", "b", "c"]},
                    "visible_for_annotators": True,
                    "dataset_id": str(terms_property.dataset_id),
                    "inserted_at": terms_property.inserted_at.isoformat(),
                    "updated_at": terms_property.updated_at.isoformat(),
                },
                {
                    "id": str(integer_property.id),
                    "name": "integer",
                    "title": integer_property.title,
                    "settings": {"type": "integer", "min": None, "max": None},
                    "visible_for_annotators": True,
                    "dataset_id": str(integer_property.dataset_id),
                    "inserted_at": integer_property.inserted_at.isoformat(),
                    "updated_at": integer_property.updated_at.isoformat(),
                },
                {
                    "id": str(float_property.id),
                    "name": "float",
                    "title": float_property.title,
                    "settings": {"type": "float", "min": None, "max": None},
                    "visible_for_annotators": True,
                    "dataset_id": str(float_property.dataset_id),
                    "inserted_at": float_property.inserted_at.isoformat(),
                    "updated_at": float_property.updated_at.isoformat(),
                },
            ]
        }

    async def test_list_current_user_dataset_metadata_properties_without_authentication(
        self, async_client: "AsyncClient"
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/me/datasets/{dataset.id}/metadata-properties")

        assert response.status_code == 401

    async def test_list_current_user_dataset_metadata_properties_as_owner(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        await TermsMetadataPropertyFactory.create(name="property-01", dataset=dataset, allowed_roles=[])
        await TermsMetadataPropertyFactory.create(name="property-02", dataset=dataset, allowed_roles=[UserRole.admin])
        await IntegerMetadataPropertyFactory.create(
            name="property-03", dataset=dataset, allowed_roles=[UserRole.annotator]
        )
        await IntegerMetadataPropertyFactory.create(
            name="property-04", dataset=dataset, allowed_roles=[UserRole.admin, UserRole.annotator]
        )
        await TermsMetadataPropertyFactory.create()
        await IntegerMetadataPropertyFactory.create()

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [metadata_property["name"] for metadata_property in response_body["items"]] == [
            "property-01",
            "property-02",
            "property-03",
            "property-04",
        ]

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_list_current_user_dataset_metadata_properties_as_restricted_user_role(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)

        await TermsMetadataPropertyFactory.create(name="allowed-property-01", dataset=dataset, allowed_roles=[role])
        await TermsMetadataPropertyFactory.create(name="allowed-property-02", dataset=dataset, allowed_roles=[role])
        await IntegerMetadataPropertyFactory.create(name="not-allowed-property-03", dataset=dataset, allowed_roles=[])
        await IntegerMetadataPropertyFactory.create(name="not-allowed-property-04", dataset=dataset, allowed_roles=[])
        await TermsMetadataPropertyFactory.create()
        await IntegerMetadataPropertyFactory.create()

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/metadata-properties", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [metadata_property["name"] for metadata_property in response_body["items"]] == [
            "allowed-property-01",
            "allowed-property-02",
        ]

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_list_current_user_dataset_metadata_properties_as_restricted_user_role_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/metadata-properties", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403

    async def test_list_current_user_dataset_metadata_properties_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        await DatasetFactory.create()

        response = await async_client.get(
            f"/api/v1/me/datasets/{uuid4()}/metadata-properties", headers=owner_auth_header
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_list_dataset_vectors_settings(self, async_client: "AsyncClient", role: UserRole):
        dataset = await DatasetFactory.create()
        vectors_settings = await VectorSettingsFactory.create_batch(size=3, dataset=dataset)
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/vectors-settings", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(vector_settings.id),
                    "name": vector_settings.name,
                    "title": vector_settings.title,
                    "dimensions": vector_settings.dimensions,
                    "dataset_id": str(vector_settings.dataset_id),
                    "inserted_at": vector_settings.inserted_at.isoformat(),
                    "updated_at": vector_settings.updated_at.isoformat(),
                }
                for vector_settings in vectors_settings
            ]
        }

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_dataset_vectors_settings_as_user_from_another_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        annotator = await UserFactory.create(role=role)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/vectors-settings", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )

        assert response.status_code == 403

    async def test_list_dataset_vectors_settings_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/vectors-settings")

        assert response.status_code == 401

    # Helper function to create records with responses

    async def test_get_dataset(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create(name="dataset")

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(dataset.id),
            "name": "dataset",
            "guidelines": None,
            "allow_extra_metadata": True,
            "status": "draft",
            "workspace_id": str(dataset.workspace_id),
            "last_activity_at": dataset.last_activity_at.isoformat(),
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
        dataset_json = {
            "name": "name",
            "guidelines": "guidelines",
            "allow_extra_metadata": False,
            "workspace_id": str(workspace.id),
        }

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
            "allow_extra_metadata": False,
            "status": "draft",
            "workspace_id": str(workspace.id),
            "last_activity_at": datetime.fromisoformat(response_body["last_activity_at"]).isoformat(),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }
        assert response_body["last_activity_at"] == response_body["inserted_at"] == response_body["updated_at"]

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
            "dataset_id": str(dataset.id),
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
            ({"type": "terms"}, {"type": "terms", "values": None}),
            ({"type": "terms", "values": ["a"]}, {"type": "terms", "values": ["a"]}),
            (
                {"type": "terms", "values": ["a", "b", "c", "d", "e"]},
                {"type": "terms", "values": ["a", "b", "c", "d", "e"]},
            ),
            ({"type": "integer"}, {"type": "integer", "min": None, "max": None}),
            ({"type": "integer", "min": 2}, {"type": "integer", "min": 2, "max": None}),
            ({"type": "integer", "max": 10}, {"type": "integer", "min": None, "max": 10}),
            ({"type": "integer", "min": 2, "max": 10}, {"type": "integer", "min": 2, "max": 10}),
            ({"type": "float"}, {"type": "float", "min": None, "max": None}),
            ({"type": "float", "min": 2}, {"type": "float", "min": 2, "max": None}),
            ({"type": "float", "max": 10}, {"type": "float", "min": None, "max": 10}),
            ({"type": "float", "min": 2, "max": 10}, {"type": "float", "min": 2, "max": 10}),
            ({"type": "float", "min": 0.3, "max": 1.0}, {"type": "float", "min": 0.3, "max": 1.0}),
        ],
    )
    async def test_create_dataset_metadata_property(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        settings: dict,
        expected_settings: dict,
    ):
        dataset = await DatasetFactory.create()
        metadata_property_json = {"name": "name", "title": "title", "settings": settings}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1

        response_body = response.json()
        assert await db.get(MetadataProperty, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "name": "name",
            "title": "title",
            "settings": expected_settings,
            "visible_for_annotators": True,
            "dataset_id": str(dataset.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    async def test_create_dataset_metadata_property_with_dataset_ready(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: "SearchEngine",
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        metadata_property_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "terms", "values": ["valueA", "valueB", "valueC"]},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1

        response_body = response.json()
        created_metadata_property = await db.get(MetadataProperty, UUID(response_body["id"]))

        assert created_metadata_property
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "visible_for_annotators": True,
            "dataset_id": str(dataset.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
            **metadata_property_json,
        }

        mock_search_engine.configure_metadata_property.assert_called_once_with(dataset, created_metadata_property)

    async def test_create_dataset_metadata_property_with_dataset_ready_and_search_engine_error(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, db: "AsyncSession", owner_auth_header: dict
    ):
        mock_search_engine.configure_metadata_property.side_effect = ValueError("MOCK")

        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        metadata_property_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "terms", "values": ["valueA", "valueB", "valueC"]},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 0

    async def test_create_dataset_metadata_property_as_admin(self, async_client: "AsyncClient", db: "AsyncSession"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)
        metadata_property_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "terms", "values": ["a", "b", "c"]},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=metadata_property_json,
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1

    @pytest.mark.parametrize(
        "settings",
        [
            None,
            {},
            {"type": "wrong-type"},
            {"type": None},
            {"type": "terms", "values": []},
            {"type": "integer", "min": 5, "max": 2},
            {"type": "float", "min": 5.0, "max": 2.0},
        ],
    )
    async def test_create_dataset_metadata_property_with_invalid_settings(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, settings: dict
    ):
        dataset = await DatasetFactory.create()
        metadata_property_json = {"name": "name", "title": "title", "settings": settings}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_metadata_property_as_admin_for_different_workspace(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])

        dataset = await DatasetFactory.create()
        metadata_property_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "terms", "values": ["a", "b", "c"]},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json=metadata_property_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    async def test_create_dataset_metadata_property_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create()
        question_json = {"name": "name", "title": "title", "settings": {"type": "terms", "values": ["a", "b", "c"]}}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json=question_json,
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Question.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "invalid_name",
        [
            None,
            "",
            "::",
            "bad Name",
            "¿pef",
            "wrong:name",
            "wrong.name" "**",
            "a" * (METADATA_PROPERTY_CREATE_NAME_MAX_LENGTH + 1),
        ],
    )
    async def test_create_dataset_metadata_property_with_invalid_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, invalid_name: str
    ):
        dataset = await DatasetFactory.create()
        metadata_property_json = {"name": invalid_name, "title": "title", "settings": {"type": "terms"}}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_metadata_property_with_existent_name(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        metadata_property = await TermsMetadataPropertyFactory.create(name="name")
        metadata_property_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "terms", "values": ["a", "b", "c"]},
        }

        response = await async_client.post(
            f"/api/v1/datasets/{metadata_property.dataset.id}/metadata-properties",
            headers=owner_auth_header,
            json=metadata_property_json,
        )

        assert response.status_code == 409
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1

    @pytest.mark.parametrize(
        "title",
        ["", "a" * (METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH + 1)],
    )
    async def test_create_dataset_metadata_property_with_invalid_title(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, title: str
    ):
        dataset = await DatasetFactory.create()
        metadata_property_json = {"name": "name", "title": title, "settings": {"type": "terms"}}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Field.id)))).scalar() == 0

    async def test_create_dataset_metadata_property_visible_for_annotators(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        metadata_property_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "terms"},
            "visible_for_annotators": True,
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1

        response_body = response.json()
        assert response_body["visible_for_annotators"] == True

        created_metadata_property = await db.get(MetadataProperty, UUID(response_body["id"]))
        assert created_metadata_property
        assert created_metadata_property.allowed_roles == [UserRole.admin, UserRole.annotator]

    async def test_create_dataset_metadata_property_not_visible_for_annotators(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        metadata_property_json = {
            "name": "name",
            "title": "title",
            "settings": {"type": "terms"},
            "visible_for_annotators": False,
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1

        response_body = response.json()
        assert response_body["visible_for_annotators"] == False

        created_metadata_property = await db.get(MetadataProperty, UUID(response_body["id"]))
        assert created_metadata_property
        assert created_metadata_property.allowed_roles == [UserRole.admin]

    async def test_create_dataset_metadata_property_without_visible_for_annotators(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        metadata_property_json = {"name": "name", "title": "title", "settings": {"type": "terms"}}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties", headers=owner_auth_header, json=metadata_property_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1

        response_body = response.json()
        assert response_body["visible_for_annotators"] == True

        created_metadata_property = await db.get(MetadataProperty, UUID(response_body["id"]))
        assert created_metadata_property
        assert created_metadata_property.allowed_roles == [UserRole.admin, UserRole.annotator]

    @pytest.mark.parametrize("values", [[], ["value"] * (TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS + 1)])
    async def test_create_dataset_terms_metadata_property_with_invalid_number_of_values(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, values: List[str]
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/metadata-properties",
            headers=owner_auth_header,
            json={"name": "name", "title": "title", "settings": {"type": "terms", "values": values}},
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 0

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    @pytest.mark.parametrize("dataset_status", [DatasetStatus.draft, DatasetStatus.ready])
    async def test_create_dataset_vector_settings(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: SearchEngine,
        role: UserRole,
        dataset_status: DatasetStatus,
    ):
        dataset = await DatasetFactory.create(status=dataset_status)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        vector_settings_json = {
            "name": "vectors-for-semantic-search",
            "title": "Vectors generated with sentence-transformers/all-MiniLM-L6-v2",
            "dimensions": 384,
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/vectors-settings",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json=vector_settings_json,
        )

        response_json = response.json()

        assert response.status_code == 201
        vector_settings = await db.get(VectorSettings, UUID(response_json["id"]))
        assert response_json == {
            "id": str(vector_settings.id),
            "name": "vectors-for-semantic-search",
            "title": "Vectors generated with sentence-transformers/all-MiniLM-L6-v2",
            "dimensions": 384,
            "dataset_id": str(vector_settings.dataset_id),
            "inserted_at": vector_settings.inserted_at.isoformat(),
            "updated_at": vector_settings.updated_at.isoformat(),
        }
        if dataset_status == DatasetStatus.draft:
            mock_search_engine.configure_index_vectors.assert_not_called()
        else:
            mock_search_engine.configure_index_vectors.assert_called_once_with(vector_settings)

    @pytest.mark.parametrize(
        "payload",
        [
            {"name": "", "title": "vectors", "dimensions": 5},
            {"name": "a" * (VECTOR_SETTINGS_CREATE_NAME_MAX_LENGTH + 1), "title": "vectors", "dimensions": 5},
            {"name": " invalid", "title": "vectors", "dimensions": 5},
            {"name": "vectors", "title": "", "dimensions": 5},
            {
                "name": "vectors",
                "title": "a" * (VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH + 1),
                "dimensions": 5,
            },
            {
                "name": "vectors",
                "title": "vectors",
                "dimensions": 0,
            },
            {"name": "vectors", "title": "vectors", "dimensions": -1},
        ],
    )
    async def test_create_dataset_vector_settings_with_invalid_settings(
        self, async_client: "AsyncClient", owner_auth_header: dict, payload: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/vectors-settings", headers=owner_auth_header, json=payload
        )

        assert response.status_code == 422

    async def test_create_dataset_vector_settings_with_existent_name(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        vector_settings = await VectorSettingsFactory.create(name="vectors")

        response = await async_client.post(
            f"/api/v1/datasets/{vector_settings.dataset_id}/vectors-settings",
            headers=owner_auth_header,
            json={"name": "vectors", "title": "vectors", "dimensions": 384},
        )

        assert response.status_code == 409

    async def test_create_dataset_vector_settings_with_non_existent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        response = await async_client.post(
            f"/api/v1/datasets/{uuid4()}/vectors-settings",
            headers=owner_auth_header,
            json={"name": "vectors", "title": "vectors", "dimensions": 384},
        )

        assert response.status_code == 404

    async def test_create_dataset_vector_settings_as_annotator(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/vectors-settings",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={
                "name": "vectors-for-search",
                "title": "Vectors generated with sentence-transformers/all-MiniLM-L6-v2",
                "dimensions": 384,
            },
        )

        assert response.status_code == 403

    async def test_create_dataset_vector_settings_as_admin_from_different_workspace(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        admin = await AdminFactory.create()

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/vectors-settings",
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json={
                "name": "vectors-for-search",
                "title": "Vectors generated with sentence-transformers/all-MiniLM-L6-v2",
                "dimensions": 384,
            },
        )

        assert response.status_code == 403

    async def test_create_dataset_vector_settings_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/vectors-settings",
            json={
                "name": "vectors-for-search",
                "dimensions": 384,
                "description": "Vectors generated with sentence-transformers/all-MiniLM-L6-v2",
            },
        )

        assert response.status_code == 401

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

        await TermsMetadataPropertyFactory.create(name="terms-metadata", dataset=dataset)
        await IntegerMetadataPropertyFactory.create(name="integer-metadata", dataset=dataset)
        await FloatMetadataPropertyFactory.create(name="float-metadata", dataset=dataset)

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
                    "metadata": {
                        "terms-metadata": "a",
                        "integer-metadata": 1,
                        "float-metadata": 1.2,
                    },
                },
                {
                    "fields": {"input": "Say Hello", "output": "Hi"},
                    "suggestions": [{"question_id": str(question_a.id), "value": "no"}],
                    "metadata": {
                        "terms-metadata": "a",
                    },
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
        mock_search_engine.index_records.assert_called_once_with(dataset, records)

        test_telemetry.track_data.assert_called_once_with(
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
        mock_search_engine.index_records.assert_called_once_with(dataset, records)

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
                    "errors": [
                        {
                            "loc": ["body", "items", 0, "responses"],
                            "msg": f"'responses' contains several responses for the same user_id='{str(owner.id)}'",
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
        assert response.json() == {
            "detail": "Record at position 0 is not valid because missing required value for field: 'output'"
        }
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
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body", "items", 0, "fields", "output"],
                            "msg": "str type expected",
                            "type": "type_error.str",
                        }
                    ]
                },
            }
        }
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
                {"fields": {"input": "Say Hello", "output": "unexpected"}},
                {"fields": {"input": "Say Hello"}},
                {"fields": {"input": "Say Pello"}},
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Record at position 0 is not valid because found fields values for non configured fields: ['output']"
        }
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "record_json",
        [
            {"fields": {"input": "text-input", "output": "text-output"}},
            {"fields": {"input": "text-input", "output": None}},
            {"fields": {"input": "text-input"}},
        ],
    )
    async def test_create_dataset_records_with_optional_fields(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, record_json: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await FieldFactory.create(name="input", dataset=dataset)
        await FieldFactory.create(name="output", dataset=dataset, required=False)

        records_json = {"items": [record_json]}

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 204, response.json()
        await db.refresh(dataset, attribute_names=["records"])
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 1

    async def test_create_dataset_records_with_wrong_optional_fields(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await FieldFactory.create(name="input", dataset=dataset)
        await FieldFactory.create(name="output", dataset=dataset, required=False)
        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"input": "text-input", "output": 1},
                },
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body", "items", 0, "fields", "output"],
                            "msg": "str type expected",
                            "type": "type_error.str",
                        }
                    ]
                },
            }
        }
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "MetadataPropertyFactoryType, settings, value",
        [
            (TermsMetadataPropertyFactory, {"values": ["a", "b", "c"]}, "c"),
            (TermsMetadataPropertyFactory, {"values": None}, "c"),
            (TermsMetadataPropertyFactory, {"values": ["a", "b", "c"]}, None),
            (TermsMetadataPropertyFactory, {"values": None}, None),
            (IntegerMetadataPropertyFactory, {"min": 0, "max": 10}, 5),
            (IntegerMetadataPropertyFactory, {"min": 0, "max": 10}, None),
            (FloatMetadataPropertyFactory, {"min": 0.0, "max": 1}, 0.5),
            (FloatMetadataPropertyFactory, {"min": 0.3, "max": 0.5}, 0.35),
            (FloatMetadataPropertyFactory, {"min": 0.3, "max": 0.9}, 0.89),
            (FloatMetadataPropertyFactory, {"min": 0.3, "max": 0.9}, None),
        ],
    )
    async def test_create_dataset_records_with_metadata_values(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        MetadataPropertyFactoryType: Type[MetadataPropertyFactory],
        settings: Dict[str, Any],
        value: Any,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="completion", dataset=dataset)
        await TextQuestionFactory.create(name="corrected", dataset=dataset)
        await MetadataPropertyFactoryType.create(name="metadata-property", settings=settings, dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"completion": "text-input"},
                    "metadata": {"metadata-property": value},
                }
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 204

        record = (await db.execute(select(Record))).scalar()
        assert record.metadata_ == {"metadata-property": value}

    @pytest.mark.parametrize(
        "MetadataPropertyFactoryType, settings",
        [
            (TermsMetadataPropertyFactory, {"values": ["a", "b", "c"]}),
            (IntegerMetadataPropertyFactory, {"min": 0, "max": 10}),
            (FloatMetadataPropertyFactory, {"min": 0.3, "max": 0.9}),
        ],
    )
    async def test_create_dataset_records_with_metadata_nan_values(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner_auth_header: dict,
        MetadataPropertyFactoryType: Type[MetadataPropertyFactory],
        settings: Dict[str, Any],
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="completion", dataset=dataset)
        await TextQuestionFactory.create(name="corrected", dataset=dataset)
        await MetadataPropertyFactoryType.create(name="metadata-property", settings=settings, dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"completion": "text-input"},
                    "metadata": {"metadata-property": math.nan},
                }
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "MetadataPropertyFactoryType, settings, value",
        [
            (TermsMetadataPropertyFactory, {"values": ["a", "b", "c"]}, "z"),
            (IntegerMetadataPropertyFactory, {"min": 0, "max": 10}, -1),
            (FloatMetadataPropertyFactory, {"min": 0.0, "max": 10.0}, -1.0),
            (FloatMetadataPropertyFactory, {"min": 0.3, "max": 0.9}, 0),
            (FloatMetadataPropertyFactory, {"min": 0.3, "max": 0.9}, 0.91),
        ],
    )
    async def test_create_dataset_records_with_not_valid_metadata_values(
        self,
        async_client: "AsyncClient",
        owner_auth_header: dict,
        MetadataPropertyFactoryType: Type[MetadataPropertyFactory],
        settings: Dict[str, Any],
        value: Any,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="completion", dataset=dataset)
        await TextQuestionFactory.create(name="corrected", dataset=dataset)
        await MetadataPropertyFactoryType.create(name="metadata-property", dataset=dataset, settings=settings)

        records_json = {
            "items": [
                {
                    "fields": {"completion": "text-input"},
                    "metadata": {"metadata-property": value},
                }
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (
            "Record at position 0 is not valid because metadata is not valid: 'metadata-property' metadata property validation failed"
            in response.json()["detail"]
        )

    async def test_create_dataset_records_with_extra_metadata_allowed(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready, allow_extra_metadata=True)
        await TextFieldFactory.create(name="completion", dataset=dataset)
        await TextQuestionFactory.create(name="corrected", dataset=dataset)
        await TermsMetadataPropertyFactory.create(name="terms-metadata")

        records_json = {
            "items": [
                {
                    "fields": {"completion": "text-input"},
                    "metadata": {"terms-metadata": "a", "extra": {"this": {"is": "extra metadata"}}},
                }
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 204

        record = (await db.execute(select(Record))).scalar()
        assert record.metadata_ == {"terms-metadata": "a", "extra": {"this": {"is": "extra metadata"}}}

    async def test_create_dataset_records_with_extra_metadata_not_allowed(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready, allow_extra_metadata=False)
        await TextFieldFactory.create(name="completion", dataset=dataset)
        await TextQuestionFactory.create(name="corrected", dataset=dataset)

        records_json = {
            "items": [
                {
                    "fields": {"completion": "text-input"},
                    "metadata": {"not-defined-metadata-property": "unit-test"},
                }
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 422
        assert (
            "Record at position 0 is not valid because metadata is not valid: 'not-defined-metadata-property' metadata"
            f" property does not exists for dataset '{dataset.id}' and extra metadata is not allowed for this dataset"
            == response.json()["detail"]
        )

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_create_dataset_records_with_vectors(
        self, async_client: "AsyncClient", db: "AsyncSession", role: UserRole
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)

        await TextFieldFactory.create(name="text", dataset=dataset)
        await TextQuestionFactory.create(name="text_ok", dataset=dataset)

        vector_settings_a = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        vector_settings_b = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "items": [
                    {
                        "fields": {"text": "The text for record A"},
                        "vectors": {vector_settings_a.name: [5, 6, 7, 8, 9]},
                    },
                    {
                        "fields": {"text": "The text for record B"},
                        "vectors": {vector_settings_a.name: [100, 101, 102, 103, 104]},
                    },
                    {
                        "fields": {"text": "The text for record C"},
                        "vectors": {vector_settings_b.name: [200, 201, 202, 203, 204]},
                    },
                ]
            },
        )

        assert response.status_code == 204
        assert (await db.execute(select(func.count(Vector.id)))).scalar() == 3

        vector_a, vector_b, vector_c = (await db.execute(select(Vector))).scalars().all()
        record_a, record_b, record_c = (await db.execute(select(Record))).scalars().all()
        assert (
            vector_a.record_id == record_a.id
            and vector_a.vector_settings_id == vector_settings_a.id
            and vector_a.value == [5, 6, 7, 8, 9]
        )
        assert (
            vector_b.record_id == record_b.id
            and vector_b.vector_settings_id == vector_settings_a.id
            and vector_b.value == [100, 101, 102, 103, 104]
        )
        assert (
            vector_c.record_id == record_c.id
            and vector_c.vector_settings_id == vector_settings_b.id
            and vector_c.value == [200, 201, 202, 203, 204]
        )

    async def test_create_dataset_records_with_invalid_vector(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="text", dataset=dataset)
        await TextQuestionFactory.create(name="text_ok", dataset=dataset)

        vector_settings = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {"text": "Text"},
                        "vectors": {vector_settings.name: [1]},
                    }
                ]
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            f"Record at position 0 is not valid because vector with name={vector_settings.name} is not valid: "
            f"vector must have {vector_settings.dimensions} elements, got 1 elements"
        )

    async def test_create_dataset_records_with_non_existent_vector_settings(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="text", dataset=dataset)
        await TextQuestionFactory.create(name="text_ok", dataset=dataset)

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {"text": "Text"},
                        "vectors": {"missing_vector": [1, 2, 3, 4, 5]},
                    }
                ]
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "Record at position 0 is not valid because vector with name=missing_vector is not valid: "
            f"vector with name=missing_vector does not exist for dataset_id={str(dataset.id)}"
        )

    async def test_create_dataset_records_with_vector_settings_id_from_another_dataset(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextFieldFactory.create(name="text", dataset=dataset)
        await TextQuestionFactory.create(name="text_ok", dataset=dataset)

        # Create vector settings in another dataset
        vector_settings = await VectorSettingsFactory.create(dimensions=5)

        response = await async_client.post(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {"text": "Text"},
                        "vectors": {vector_settings.name: [1, 2, 3, 4, 5]},
                    }
                ]
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            f"Record at position 0 is not valid because vector with name={vector_settings.name} is not valid: "
            f"vector with name={vector_settings.name} does not exist for dataset_id={dataset.id}"
        )

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
                    "fields": {"input": "Say Hello", "output": "Hello"},
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
        mock_search_engine.index_records.assert_called_once_with(dataset, records)

        test_telemetry.track_data.assert_called_once_with(
            action="DatasetRecordsCreated", data={"records": len(records_json["items"])}
        )

    async def test_create_dataset_records_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        annotator = await AnnotatorFactory.create()
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
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

    async def test_create_dataset_records_as_admin_from_another_workspace(self, async_client: "AsyncClient"):
        admin = await AdminFactory.create()
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        records_json = {
            "items": [
                {
                    "fields": {"input": "Say Hello", "output": "Hello"},
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
            f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: admin.api_key}, json=records_json
        )

        assert response.status_code == 403

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
                    "fields": {"input": "Say Hello", "output": "Hello"},
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

    async def test_create_dataset_records_with_draft_response(
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
                            "status": "draft",
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
            await db.execute(select(func.count(Response.id)).filter(Response.status == ResponseStatus.draft))
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
                    "fields": {"input": "Say Hello", "output": "Hello"},
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
                {"fields": {"input": "Say Hello", "output": "Hello"}, "external_id": "1"},
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
                    "fields": {"input": "Say Hello", "output": "Hello"},
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
                    "fields": {"input": "Say Hello", "output": "Hello"},
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
                {"fields": {"input": "Say Hello", "output": "Hello"}, "external_id": 1},
                {"fields": "invalid", "external_id": 2},
                {"fields": {"input": "Say Hello", "output": "Hello"}, "external_id": 3},
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
                {"fields": {"input": "Say Hello", "output": "Hello"}, "external_id": 1},
                {"fields": {"input": "Say Hello", "output": "Hello"}, "external_id": 2},
            ]
        }

        response = await async_client.post(
            f"/api/v1/datasets/{uuid4()}/records", headers=owner_auth_header, json=records_json
        )

        assert response.status_code == 404
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_update_dataset_records(
        self, async_client: "AsyncClient", mock_search_engine: "SearchEngine", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)
        await TermsMetadataPropertyFactory.create(name="terms-metadata-property", dataset=dataset)
        await IntegerMetadataPropertyFactory.create(name="integer-metadata-property", dataset=dataset)
        await FloatMetadataPropertyFactory.create(name="float-metadata-property", dataset=dataset)
        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            metadata_={"terms-metadata-property": "z", "integer-metadata-property": 1, "float-metadata-property": 1.0},
        )

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "items": [
                    {
                        "id": str(records[0].id),
                        "metadata": {
                            "terms-metadata-property": None,
                            "integer-metadata-property": 0,
                            "float-metadata-property": 0.0,
                            "extra-metadata": None,
                        },
                    },
                    {
                        "id": str(records[1].id),
                        "metadata": {
                            "terms-metadata-property": "b",
                            "integer-metadata-property": None,
                            "float-metadata-property": 1.0,
                            "extra-metadata": "yes",
                        },
                    },
                    {
                        "id": str(records[2].id),
                        "metadata": {
                            "terms-metadata-property": "c",
                            "integer-metadata-property": 2,
                            "float-metadata-property": None,
                            "extra-metadata": "yes",
                        },
                    },
                    {
                        "id": str(records[3].id),
                    },
                ]
            },
        )

        assert response.status_code == 204

        # Record 0
        assert records[0].metadata_ == {
            "terms-metadata-property": None,
            "integer-metadata-property": 0,
            "float-metadata-property": 0.0,
            "extra-metadata": None,
        }

        # Record 1
        assert records[1].metadata_ == {
            "terms-metadata-property": "b",
            "integer-metadata-property": None,
            "float-metadata-property": 1.0,
            "extra-metadata": "yes",
        }

        # Record 2
        assert records[2].metadata_ == {
            "terms-metadata-property": "c",
            "integer-metadata-property": 2,
            "float-metadata-property": None,
            "extra-metadata": "yes",
        }

        # Record 3
        assert records[3].metadata_ == {
            "terms-metadata-property": "z",
            "integer-metadata-property": 1,
            "float-metadata-property": 1.0,
        }

        # it should be called only with the first three records (metadata was updated for them)
        mock_search_engine.index_records.assert_called_once_with(dataset, records[:3])

    async def test_update_dataset_records_with_suggestions(
        self, async_client: "AsyncClient", mock_search_engine: "SearchEngine", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_0 = await TextQuestionFactory.create(dataset=dataset)
        question_1 = await TextQuestionFactory.create(dataset=dataset)
        question_2 = await TextQuestionFactory.create(dataset=dataset)
        records = await RecordFactory.create_batch(10, dataset=dataset)

        # Record 0 suggestions (should be deleted)
        suggestions_records_0 = [
            await SuggestionFactory.create(question=question_0, record=records[0], value="suggestion 0 1"),
            await SuggestionFactory.create(question=question_1, record=records[0], value="suggestion 0 2"),
            await SuggestionFactory.create(question=question_2, record=records[0], value="suggestion 0 3"),
        ]

        # Record 1 suggestions (should be deleted)
        suggestions_records_1 = [
            await SuggestionFactory.create(question=question_0, record=records[1], value="suggestion 1 1"),
            await SuggestionFactory.create(question=question_1, record=records[1], value="suggestion 1 2"),
            await SuggestionFactory.create(question=question_2, record=records[1], value="suggestion 1 3"),
        ]

        # Record 2 suggestions (should be kept)
        suggestions_records_2 = [
            await SuggestionFactory.create(question=question_0, record=records[2], value="suggestion 2 1"),
            await SuggestionFactory.create(question=question_1, record=records[2], value="suggestion 2 2"),
            await SuggestionFactory.create(question=question_2, record=records[2], value="suggestion 2 3"),
        ]

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(records[0].id),
                        "suggestions": [
                            {
                                "question_id": str(question_0.id),
                                "value": "suggestion updated 0 1",
                            },
                            {
                                "question_id": str(question_1.id),
                                "value": "suggestion updated 0 2",
                            },
                            {"question_id": str(question_2.id), "value": "suggestion updated 0 3"},
                        ],
                    },
                    {
                        "id": str(records[1].id),
                        "suggestions": [
                            {
                                "question_id": str(question_0.id),
                                "value": "suggestion updated 1 1",
                            }
                        ],
                    },
                    {
                        "id": str(records[2].id),
                    },
                    {
                        "id": str(records[3].id),
                        "suggestions": [
                            {
                                "question_id": str(question_0.id),
                                "value": "suggestion updated 3 1",
                            },
                            {
                                "question_id": str(question_1.id),
                                "value": "suggestion updated 3 2",
                            },
                            {"question_id": str(question_2.id), "value": "suggestion updated 3 3"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 204

        # Record 0
        await records[0].awaitable_attrs.suggestions
        assert records[0].suggestions[0].value == "suggestion updated 0 1"
        assert records[0].suggestions[1].value == "suggestion updated 0 2"
        assert records[0].suggestions[2].value == "suggestion updated 0 3"
        for suggestion in suggestions_records_0:
            assert inspect(suggestion).deleted

        # Record 1
        await records[1].awaitable_attrs.suggestions
        assert records[1].suggestions[0].value == "suggestion updated 1 1"
        for suggestion in suggestions_records_1:
            assert inspect(suggestion).deleted

        # Record 2
        for suggestion in suggestions_records_2:
            assert inspect(suggestion).persistent

        # Record 3
        await records[3].awaitable_attrs.suggestions
        assert records[3].suggestions[0].value == "suggestion updated 3 1"
        assert records[3].suggestions[1].value == "suggestion updated 3 2"
        assert records[3].suggestions[2].value == "suggestion updated 3 3"

        mock_search_engine.index_records.assert_not_called()

    async def test_update_dataset_records_with_empty_list_of_suggestions(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question_0 = await TextQuestionFactory.create(dataset=dataset)
        question_1 = await TextQuestionFactory.create(dataset=dataset)
        question_2 = await TextQuestionFactory.create(dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        suggestions_records_0 = [
            await SuggestionFactory.create(question=question_0, record=record, value="suggestion 0 1"),
            await SuggestionFactory.create(question=question_1, record=record, value="suggestion 0 2"),
            await SuggestionFactory.create(question=question_2, record=record, value="suggestion 0 3"),
        ]

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={"items": [{"id": str(record.id), "suggestions": []}]},
        )

        assert response.status_code == 204

        assert await record.awaitable_attrs.suggestions == []
        for suggestion in suggestions_records_0:
            assert inspect(suggestion).deleted

    async def test_update_dataset_records_with_vectors(
        self, async_client: "AsyncClient", mock_search_engine: "SearchEngine", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        vector_settings_0 = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        vector_settings_1 = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        vector_settings_2 = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        records = await RecordFactory.create_batch(10, dataset=dataset)

        # Record 0 vectors (all should be updated)
        await VectorFactory.create(vector_settings=vector_settings_0, record=records[0], value=[0, 0, 0, 0, 0])
        await VectorFactory.create(vector_settings=vector_settings_1, record=records[0], value=[1, 1, 1, 1, 1])
        await VectorFactory.create(vector_settings=vector_settings_2, record=records[0], value=[2, 2, 2, 2, 2])

        # Record 1 vectors (just the first one should be updated)
        await VectorFactory.create(vector_settings=vector_settings_0, record=records[1], value=[3, 3, 3, 3, 3])
        await VectorFactory.create(vector_settings=vector_settings_1, record=records[1], value=[4, 4, 4, 4, 4])
        await VectorFactory.create(vector_settings=vector_settings_2, record=records[1], value=[5, 5, 5, 5, 5])

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(records[0].id),
                        "vectors": {
                            vector_settings_0.name: [0.1, 0.1, 0.1, 0.1, 0.1],
                            vector_settings_1.name: [1.1, 1.1, 1.1, 1.1, 1.1],
                            vector_settings_2.name: [2.1, 2.1, 2.1, 2.1, 2.1],
                        },
                    },
                    {
                        "id": str(records[1].id),
                        "vectors": {
                            vector_settings_0.name: [3.1, 3.1, 3.1, 3.1, 3.1],
                        },
                    },
                    {
                        "id": str(records[2].id),
                        "vectors": {
                            vector_settings_0.name: [4.1, 4.1, 4.1, 4.1, 4.1],
                            vector_settings_1.name: [5.1, 5.1, 5.1, 5.1, 5.1],
                            vector_settings_2.name: [6.1, 6.1, 6.1, 6.1, 6.1],
                        },
                    },
                ]
            },
        )

        assert response.status_code == 204

        # Record 0
        await records[0].awaitable_attrs.vectors
        assert records[0].vectors[0].value == [0.1, 0.1, 0.1, 0.1, 0.1]
        assert records[0].vectors[1].value == [1.1, 1.1, 1.1, 1.1, 1.1]
        assert records[0].vectors[2].value == [2.1, 2.1, 2.1, 2.1, 2.1]

        # Record 1
        await records[1].awaitable_attrs.vectors
        assert records[1].vectors[0].value == [3.1, 3.1, 3.1, 3.1, 3.1]
        assert records[1].vectors[1].value == [4, 4, 4, 4, 4]
        assert records[1].vectors[2].value == [5, 5, 5, 5, 5]

        # Record 2
        await records[2].awaitable_attrs.vectors
        assert records[2].vectors[0].value == [4.1, 4.1, 4.1, 4.1, 4.1]
        assert records[2].vectors[1].value == [5.1, 5.1, 5.1, 5.1, 5.1]
        assert records[2].vectors[2].value == [6.1, 6.1, 6.1, 6.1, 6.1]

        mock_search_engine.index_records.assert_called_once_with(dataset, records[:3])

    async def test_update_dataset_records_with_invalid_metadata(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TermsMetadataPropertyFactory.create(dataset=dataset, name="terms")
        records = await RecordFactory.create_batch(5, dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(records[0].id),
                        "metadata": {
                            "terms": "a",
                        },
                    },
                    {
                        "id": str(records[1].id),
                        "metadata": {
                            "terms": "i was not declared",
                        },
                    },
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Record at position 1 is not valid because metadata is not valid: 'terms' metadata property "
            "validation failed because 'i was not declared' is not an allowed term."
        }

    async def test_update_dataset_records_with_metadata_nan_value(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TermsMetadataPropertyFactory.create(dataset=dataset, name="terms")
        await FloatMetadataPropertyFactory.create(dataset=dataset, name="float")
        records = await RecordFactory.create_batch(3, dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(records[0].id),
                        "metadata": {"terms": math.nan},
                    },
                    {
                        "id": str(records[1].id),
                        "metadata": {"float": math.nan},
                    },
                    {
                        "id": str(records[2].id),
                        "metadata": {"terms": "a"},
                    },
                ]
            },
        )

        assert response.status_code == 422

    async def test_update_dataset_records_with_invalid_suggestions(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question = await LabelSelectionQuestionFactory.create(dataset=dataset)
        records = await RecordFactory.create_batch(5, dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {"id": str(records[0].id), "suggestions": [{"question_id": str(question.id), "value": "option-a"}]},
                    {
                        "id": str(records[1].id),
                        "suggestions": [{"question_id": str(question.id), "value": "not-valid-option"}],
                    },
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Record at position 0 is not valid because suggestion for question_id={question.id} is not valid: 'option-a' is not a valid label for label selection question.\nValid labels are: ['option1', 'option2', 'option3']"
        }

    async def test_update_dataset_records_with_invalid_vectors(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        vector_settings = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        records = await RecordFactory.create_batch(5, dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {"id": str(records[1].id), "vectors": {vector_settings.name: [0.0, 1.0, 2.0, 3.0, 4.0, 6.0]}},
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Record at position 0 is not valid because vector with name={vector_settings.name} is not "
            "valid: vector must have 5 elements, got 6 elements"
        }

    async def test_update_dataset_records_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset_id = uuid4()

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset_id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(uuid4()),
                    }
                ]
            },
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Dataset with id `{dataset_id}` not found"}

    async def test_update_dataset_records_with_nonexistent_records(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        records = [{"id": str(uuid4()), "metadata": {"i exists": False}} for _ in range(3)]

        records.append({"id": str(record.id), "metadata": {"i exists": True}})

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={"items": records},
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Found records that do not exist: {records[0]['id']}, {records[1]['id']}, {records[2]['id']}"
        }

    async def test_update_dataset_records_with_nonexistent_question_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        question_id = str(uuid4())

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {"id": str(record.id), "suggestions": [{"question_id": question_id, "value": "shit"}]},
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Record at position 0 is not valid because suggestion for question_id={question_id} is not "
            f"valid: question_id={question_id} does not exist"
        }

    async def test_update_dataset_records_with_nonexistent_vector_settings_name(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={"items": [{"id": str(record.id), "vectors": {"i-do-not-exist": [1, 2, 3, 4]}}]},
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Record at position 0 is not valid because vector with name=i-do-not-exist is not valid: vector "
            f"with name=i-do-not-exist does not exist for dataset_id={dataset.id}"
        }

    async def test_update_dataset_records_with_duplicate_records_ids(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {"id": str(record.id)},
                    {"id": str(record.id)},
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "Found duplicate records IDs"}

    async def test_update_dataset_records_with_duplicate_suggestions_question_ids(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question = await TextQuestionFactory.create(dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "suggestions": [
                            {"question_id": str(question.id), "value": "a"},
                            {"question_id": str(question.id), "value": "b"},
                        ],
                    },
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Record at position 0 is not valid because found duplicate suggestions question IDs"
        }

    async def test_update_dataset_records_as_admin_from_another_workspace(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(role=UserRole.admin)

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "items": [
                    {
                        "id": str(uuid4()),
                    }
                ]
            },
        )

        assert response.status_code == 403

    async def test_update_dataset_records_as_annotator(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(role=UserRole.annotator, workspaces=[dataset.workspace])

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "items": [
                    {
                        "id": str(uuid4()),
                    }
                ]
            },
        )

        assert response.status_code == 403

    async def test_update_dataset_records_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.patch(
            f"/api/v1/datasets/{dataset.id}/records", json={"items": [{"id": str(uuid4())}]}
        )

        assert response.status_code == 401

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

    async def test_search_current_user_dataset_records(
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
            query=TextQuery(q="Hello", field="input"),
            metadata_filters=[],
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=None,
            user_id=owner.id,
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
                        "dataset_id": str(records[0].dataset_id),
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
                        "dataset_id": str(records[1].dataset_id),
                        "inserted_at": records[1].inserted_at.isoformat(),
                        "updated_at": records[1].updated_at.isoformat(),
                    },
                    "query_score": 12.2,
                },
            ],
            "total": 2,
        }

    @pytest.mark.parametrize(
        ("property_config", "param_value", "expected_filter_class", "expected_filter_args"),
        [
            (
                {"name": "terms_prop", "settings": {"type": "terms"}},
                "value",
                TermsMetadataFilter,
                dict(values=["value"]),
            ),
            (
                {"name": "terms_prop", "settings": {"type": "terms"}},
                "value1,value2",
                TermsMetadataFilter,
                dict(values=["value1", "value2"]),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"ge": 10, "le": 20}',
                IntegerMetadataFilter,
                dict(ge=10, le=20),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"ge": 20}',
                IntegerMetadataFilter,
                dict(ge=20, high=None),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"le": 20}',
                IntegerMetadataFilter,
                dict(low=None, le=20),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"ge": -1.30, "le": 23.23}',
                FloatMetadataFilter,
                dict(ge=-1.30, le=23.23),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"ge": 23.23}',
                FloatMetadataFilter,
                dict(ge=23.23, high=None),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"le": 11.32}',
                FloatMetadataFilter,
                dict(low=None, le=11.32),
            ),
        ],
    )
    async def test_search_current_user_dataset_records_with_metadata_filter(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
        property_config: dict,
        param_value: str,
        expected_filter_class: Type[MetadataFilter],
        expected_filter_args: dict,
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)

        metadata_property = await MetadataPropertyFactory.create(
            name=property_config["name"],
            settings=property_config["settings"],
            dataset=dataset,
        )

        mock_search_engine.search.return_value = SearchResponses(
            total=2,
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
        )

        params = {"metadata": [f"{metadata_property.name}:{param_value}"]}

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            params=params,
            headers=owner_auth_header,
            json=query_json,
        )
        assert response.status_code == 200, response.json()

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=TextQuery(q="Hello", field="input"),
            metadata_filters=[expected_filter_class(metadata_property=metadata_property, **expected_filter_args)],
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=None,
            user_id=owner.id,
        )

    @pytest.mark.parametrize(
        ("property_config", "wrong_value"),
        [
            ({"name": "terms_prop", "settings": {"type": "terms"}}, None),
            ({"name": "terms_prop", "settings": {"type": "terms"}}, "terms_prop"),
            ({"name": "terms_prop", "settings": {"type": "terms"}}, "terms_prop:"),
            ({"name": "terms_prop", "settings": {"type": "terms"}}, "wrong-value"),
            ({"name": "integer_prop", "settings": {"type": "integer"}}, None),
            ({"name": "integer_prop", "settings": {"type": "integer"}}, "integer_prop"),
            ({"name": "integer_prop", "settings": {"type": "integer"}}, "integer_prop:"),
            ({"name": "integer_prop", "settings": {"type": "integer"}}, "integer_prop:{}"),
            ({"name": "integer_prop", "settings": {"type": "integer"}}, "wrong-value"),
            ({"name": "float_prop", "settings": {"type": "float"}}, None),
            ({"name": "float_prop", "settings": {"type": "float"}}, "float_prop"),
            ({"name": "float_prop", "settings": {"type": "float"}}, "float_prop:"),
            ({"name": "float_prop", "settings": {"type": "float"}}, "float_prop:{}"),
            ({"name": "float_prop", "settings": {"type": "float"}}, "wrong-value"),
        ],
    )
    async def test_search_current_user_dataset_records_with_wrong_metadata_filter_values(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
        property_config: dict,
        wrong_value: str,
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)

        await MetadataPropertyFactory.create(
            name=property_config["name"],
            settings=property_config["settings"],
            dataset=dataset,
        )

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        params = {"metadata": [wrong_value]}

        query_json = {"query": {"text": {"q": "Hello"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            params=params,
            headers=owner_auth_header,
            json=query_json,
        )
        assert response.status_code == 422, response.json()

    @pytest.mark.parametrize(
        "sorts",
        [
            [("inserted_at", None)],
            [("inserted_at", "asc")],
            [("inserted_at", "desc")],
            [("updated_at", None)],
            [("updated_at", "asc")],
            [("updated_at", "desc")],
            [("metadata.terms-metadata-property", None)],
            [("metadata.terms-metadata-property", "asc")],
            [("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "asc"), ("updated_at", "desc")],
            [("inserted_at", "desc"), ("updated_at", "asc")],
            [("inserted_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("updated_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("inserted_at", "asc"), ("updated_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("inserted_at", "desc"), ("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "asc"), ("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
        ],
    )
    async def test_search_current_user_dataset_records_with_sort_by(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        owner: "User",
        owner_auth_header: dict,
        sorts: List[Tuple[str, Union[str, None]]],
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)

        expected_sorts_by = []
        for field, order in sorts:
            if field not in ("inserted_at", "updated_at"):
                field = await TermsMetadataPropertyFactory.create(name=field.split(".")[-1], dataset=dataset)
            expected_sorts_by.append(SortBy(field=field, order=order or "asc"))

        mock_search_engine.search.return_value = SearchResponses(
            total=2,
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
        )

        query_params = {
            "sort_by": [f"{field}:{order}" if order is not None else f"{field}:asc" for field, order in sorts]
        }

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            params=query_params,
            headers=owner_auth_header,
            json=query_json,
        )
        assert response.status_code == 200
        assert response.json()["total"] == 2

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=TextQuery(q="Hello", field="input"),
            metadata_filters=[],
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=expected_sorts_by,
            user_id=owner.id,
        )

    async def test_search_current_user_dataset_records_with_sort_by_with_wrong_sort_order_value(
        self, async_client: "AsyncClient", owner: "User", owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, *_ = await self.create_dataset_with_user_responses(owner, workspace)

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            params={"sort_by": "inserted_at:wrong"},
            headers=owner_auth_header,
            json=query_json,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Provided sort order in 'sort_by' query param 'wrong' for field 'inserted_at' is not valid."
        }

    async def test_search_current_user_dataset_records_with_sort_by_with_non_existent_metadata_property(
        self, async_client: "AsyncClient", owner: "User", owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, *_ = await self.create_dataset_with_user_responses(owner, workspace)

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            params={"sort_by": "metadata.i-do-not-exist:asc"},
            headers=owner_auth_header,
            json=query_json,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Provided metadata property in 'sort_by' query param 'i-do-not-exist' not found in dataset with '{dataset.id}'."
        }

    async def test_search_current_user_dataset_records_with_sort_by_with_invalid_field(
        self, async_client: "AsyncClient", owner: "User", owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, *_ = await self.create_dataset_with_user_responses(owner, workspace)

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            params={"sort_by": "not-valid"},
            headers=owner_auth_header,
            json=query_json,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Provided sort field in 'sort_by' query param 'not-valid' is not valid. "
            "It must be either 'inserted_at', 'updated_at' or `metadata.metadata-property-name`"
        }

    @pytest.mark.parametrize(
        "includes",
        [
            [],
            ["responses"],
            ["suggestions"],
            ["responses", "suggestions"],
            ["responses", "suggestions"],
        ],
    )
    async def test_search_current_user_dataset_records_with_include(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: "User", includes: List[str]
    ):
        workspace = await WorkspaceFactory.create()
        (
            dataset,
            questions,
            records,
            responses,
            suggestions,
        ) = await self.create_dataset_with_user_responses(owner, workspace)
        suggestion_a, suggestion_b = suggestions

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
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
                        "dataset_id": str(records[0].dataset_id),
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
                        "dataset_id": str(records[1].dataset_id),
                        "inserted_at": records[1].inserted_at.isoformat(),
                        "updated_at": records[1].updated_at.isoformat(),
                    },
                    "query_score": 12.2,
                },
            ],
            "total": 2,
        }

        if "responses" in includes:
            first_owner_response, second_owner_response = [
                response for response in responses if response.user_id == owner.id
            ]
            expected["items"][0]["record"]["responses"] = [
                {
                    "id": str(first_owner_response.id),
                    "values": None,
                    "status": "discarded",
                    "record_id": str(records[0].id),
                    "user_id": str(owner.id),
                    "inserted_at": first_owner_response.inserted_at.isoformat(),
                    "updated_at": first_owner_response.updated_at.isoformat(),
                }
            ]
            expected["items"][1]["record"]["responses"] = [
                {
                    "id": str(second_owner_response.id),
                    "values": {
                        "input_ok": {"value": "no"},
                        "output_ok": {"value": "no"},
                    },
                    "status": "submitted",
                    "record_id": str(records[1].id),
                    "user_id": str(owner.id),
                    "inserted_at": second_owner_response.inserted_at.isoformat(),
                    "updated_at": second_owner_response.updated_at.isoformat(),
                },
            ]

        if "suggestions" in includes:
            expected["items"][0]["record"]["suggestions"] = [
                {
                    "id": str(suggestion_a.id),
                    "value": "option-1",
                    "score": None,
                    "agent": None,
                    "type": None,
                    "question_id": str(questions[0].id),
                    "inserted_at": suggestion_a.inserted_at.isoformat(),
                    "updated_at": suggestion_a.updated_at.isoformat(),
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
                    "inserted_at": suggestion_b.inserted_at.isoformat(),
                    "updated_at": suggestion_b.updated_at.isoformat(),
                }
            ]

        query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers={API_KEY_HEADER_NAME: owner.api_key},
            json=query_json,
            params={"include": includes},
        )

        assert response.status_code == 200
        assert response.json() == expected

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=TextQuery(q="Hello", field="input"),
            metadata_filters=[],
            sort_by=None,
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            user_id=owner.id,
        )

    async def test_search_current_user_dataset_records_with_include_vectors(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        vector_settings_a = await VectorSettingsFactory.create(name="vector-a", dimensions=3, dataset=dataset)
        vector_settings_b = await VectorSettingsFactory.create(name="vector-b", dimensions=2, dataset=dataset)

        await VectorFactory.create(value=[1.0, 2.0, 3.0], vector_settings=vector_settings_a, record=record_a)
        await VectorFactory.create(value=[4.0, 5.0], vector_settings=vector_settings_b, record=record_a)
        await VectorFactory.create(value=[1.0, 2.0], vector_settings=vector_settings_b, record=record_b)

        await TextFieldFactory.create(name="input", dataset=dataset)

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=record_a.id, score=10.0),
                SearchResponseItem(record_id=record_b.id, score=9.0),
                SearchResponseItem(record_id=record_c.id, score=8.0),
            ],
            total=3,
        )

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            params={"include": RecordInclude.vectors.value},
            json={
                "query": {
                    "text": {
                        "q": "query",
                        "field": "input",
                    }
                }
            },
        )

        assert response.status_code == 200, response.text
        assert response.json() == {
            "items": [
                {
                    "record": {
                        "id": str(record_a.id),
                        "fields": {"text": "This is a text", "sentiment": "neutral"},
                        "metadata": None,
                        "external_id": record_a.external_id,
                        "vectors": {
                            "vector-a": [1.0, 2.0, 3.0],
                            "vector-b": [4.0, 5.0],
                        },
                        "dataset_id": str(record_a.dataset_id),
                        "inserted_at": record_a.inserted_at.isoformat(),
                        "updated_at": record_a.updated_at.isoformat(),
                    },
                    "query_score": 10.0,
                },
                {
                    "record": {
                        "id": str(record_b.id),
                        "fields": {"text": "This is a text", "sentiment": "neutral"},
                        "metadata": None,
                        "external_id": record_b.external_id,
                        "vectors": {
                            "vector-b": [1.0, 2.0],
                        },
                        "dataset_id": str(record_b.dataset_id),
                        "inserted_at": record_b.inserted_at.isoformat(),
                        "updated_at": record_b.updated_at.isoformat(),
                    },
                    "query_score": 9.0,
                },
                {
                    "record": {
                        "id": str(record_c.id),
                        "fields": {"text": "This is a text", "sentiment": "neutral"},
                        "metadata": None,
                        "external_id": record_c.external_id,
                        "vectors": {},
                        "dataset_id": str(record_c.dataset_id),
                        "inserted_at": record_c.inserted_at.isoformat(),
                        "updated_at": record_c.updated_at.isoformat(),
                    },
                    "query_score": 8.0,
                },
            ],
            "total": 3,
        }

    async def test_search_current_user_dataset_records_with_include_specific_vectors(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        vector_settings_a = await VectorSettingsFactory.create(name="vector-a", dimensions=3, dataset=dataset)
        vector_settings_b = await VectorSettingsFactory.create(name="vector-b", dimensions=2, dataset=dataset)
        vector_settings_c = await VectorSettingsFactory.create(name="vector-c", dimensions=4, dataset=dataset)

        await VectorFactory.create(value=[1.0, 2.0, 3.0], vector_settings=vector_settings_a, record=record_a)
        await VectorFactory.create(value=[4.0, 5.0], vector_settings=vector_settings_b, record=record_a)
        await VectorFactory.create(value=[6.0, 7.0, 8.0, 9.0], vector_settings=vector_settings_c, record=record_a)
        await VectorFactory.create(value=[1.0, 2.0], vector_settings=vector_settings_b, record=record_b)
        await VectorFactory.create(value=[10.0, 11.0, 12.0, 13.0], vector_settings=vector_settings_c, record=record_b)
        await VectorFactory.create(value=[14.0, 15.0, 16.0, 17.0], vector_settings=vector_settings_c, record=record_c)

        await TextFieldFactory.create(name="input", dataset=dataset)

        mock_search_engine.search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=record_a.id, score=10.0),
                SearchResponseItem(record_id=record_b.id, score=9.0),
                SearchResponseItem(record_id=record_c.id, score=8.0),
            ],
            total=3,
        )

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            params={"include": f"{RecordInclude.vectors.value}:{vector_settings_a.name},{vector_settings_b.name}"},
            json={
                "query": {
                    "text": {
                        "q": "query",
                        "field": "input",
                    }
                }
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "record": {
                        "id": str(record_a.id),
                        "fields": {"text": "This is a text", "sentiment": "neutral"},
                        "metadata": None,
                        "external_id": record_a.external_id,
                        "vectors": {
                            "vector-a": [1.0, 2.0, 3.0],
                            "vector-b": [4.0, 5.0],
                        },
                        "dataset_id": str(record_a.dataset_id),
                        "inserted_at": record_a.inserted_at.isoformat(),
                        "updated_at": record_a.updated_at.isoformat(),
                    },
                    "query_score": 10.0,
                },
                {
                    "record": {
                        "id": str(record_b.id),
                        "fields": {"text": "This is a text", "sentiment": "neutral"},
                        "metadata": None,
                        "external_id": record_b.external_id,
                        "vectors": {
                            "vector-b": [1.0, 2.0],
                        },
                        "dataset_id": str(record_b.dataset_id),
                        "inserted_at": record_b.inserted_at.isoformat(),
                        "updated_at": record_b.updated_at.isoformat(),
                    },
                    "query_score": 9.0,
                },
                {
                    "record": {
                        "id": str(record_c.id),
                        "fields": {"text": "This is a text", "sentiment": "neutral"},
                        "metadata": None,
                        "external_id": record_c.external_id,
                        "vectors": {},
                        "dataset_id": str(record_c.dataset_id),
                        "inserted_at": record_c.inserted_at.isoformat(),
                        "updated_at": record_c.updated_at.isoformat(),
                    },
                    "query_score": 8.0,
                },
            ],
            "total": 3,
        }

    async def test_search_current_user_dataset_records_with_response_status_filter(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, *_ = await self.create_dataset_with_user_responses(owner, workspace)
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
            query=TextQuery(q="Hello", field="input"),
            metadata_filters=[],
            user_response_status_filter=UserResponseStatusFilter(user=owner, statuses=[ResponseStatusFilter.submitted]),
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=None,
            user_id=owner.id,
        )
        assert response.status_code == 200

    async def test_search_current_user_dataset_records_with_record_vector(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)
        vector_settings = await VectorSettingsFactory.create(dataset=dataset)
        vector = await VectorFactory(record=records[0], vector_settings=vector_settings, value=[1, 2, 3])

        mock_search_engine.similarity_search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        query_json = {"query": {"vector": {"name": vector_settings.name, "record_id": str(records[0].id)}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"offset": 0, "limit": 5},
        )

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json["items"]) == 2
        assert response_json["total"] == 2

        mock_search_engine.search.assert_not_called()
        mock_search_engine.similarity_search.assert_called_once_with(
            dataset=dataset,
            vector_settings=vector_settings,
            record=records[0],
            value=None,
            query=None,
            order=SimilarityOrder.most_similar,
            max_results=5,
            metadata_filters=[],
            user_response_status_filter=None,
        )

    async def test_search_current_user_dataset_records_with_vector_value(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)
        vector_settings = await VectorSettingsFactory.create(dataset=dataset)
        selected_vector = await VectorFactory.create(
            vector_settings=vector_settings, record=records[0], value=[1, 2, 3]
        )

        mock_search_engine.similarity_search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        query_json = {"query": {"vector": {"name": vector_settings.name, "value": selected_vector.value}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"offset": 0, "limit": 10},
        )

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json["items"]) == 2
        assert response_json["total"] == 2

        mock_search_engine.search.assert_not_called()
        mock_search_engine.similarity_search.assert_called_once_with(
            dataset=dataset,
            vector_settings=vector_settings,
            record=None,
            value=selected_vector.value,
            query=None,
            order=SimilarityOrder.most_similar,
            max_results=10,
            metadata_filters=[],
            user_response_status_filter=None,
        )

    async def test_search_current_user_dataset_records_with_vector_value_and_query(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)
        vector_settings = await VectorSettingsFactory.create(dataset=dataset)
        selected_vector = await VectorFactory.create(
            vector_settings=vector_settings, record=records[0], value=[1.0, 2.0, 3.0]
        )

        mock_search_engine.similarity_search.return_value = SearchResponses(
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
            total=2,
        )

        query_json = {
            "query": {
                "text": {"q": "Test query"},
                "vector": {"name": vector_settings.name, "value": selected_vector.value},
            }
        }
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"offset": 0, "limit": 10},
        )

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json["items"]) == 2
        assert response_json["total"] == 2

        mock_search_engine.search.assert_not_called()
        mock_search_engine.similarity_search.assert_called_once_with(
            dataset=dataset,
            vector_settings=vector_settings,
            record=None,
            value=selected_vector.value,
            query=TextQuery(q="Test query"),
            order=SimilarityOrder.most_similar,
            max_results=10,
            metadata_filters=[],
            user_response_status_filter=None,
        )

    async def test_search_current_user_dataset_records_with_wrong_vector(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)
        vector_settings = await VectorSettingsFactory.create(dataset=dataset)

        query_json = {"query": {"vector": {"name": "wrong_vector", "record_id": str(records[0].id)}}}

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"offset": 0, "limit": 10},
        )

        assert response.status_code == 422
        response_json = response.json()
        assert response_json == {"detail": f"Vector `wrong_vector` not found in dataset `{dataset.id}`."}

    async def test_search_current_user_dataset_records_with_nonexistent_vector_record_id(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)
        vector_settings = await VectorSettingsFactory.create(dataset=dataset)
        wrong_record_id = str(uuid.uuid4())

        query_json = {"query": {"vector": {"name": vector_settings.name, "record_id": wrong_record_id}}}

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"offset": 0, "limit": 10},
        )

        assert response.status_code == 422
        response_json = response.json()
        assert response_json == {"detail": f"Record with id `{wrong_record_id}` not found in dataset `{dataset.id}`."}

    async def test_search_current_user_dataset_records_with_vector_record_id_from_other_dataset(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)
        vector_settings = await VectorSettingsFactory.create(dataset=dataset)
        record = await RecordFactory.create()

        query_json = {"query": {"vector": {"name": vector_settings.name, "record_id": str(record.id)}}}

        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers=owner_auth_header,
            json=query_json,
            params={"offset": 0, "limit": 10},
        )

        assert response.status_code == 422
        response_json = response.json()
        assert response_json == {"detail": f"Record with id `{record.id}` not found in dataset `{dataset.id}`."}

    async def test_search_current_user_dataset_records_with_offset_and_limit(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, *_ = await self.create_dataset_with_user_responses(owner, workspace)

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

        assert response.status_code == 200

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=TextQuery(q="Hello", field="input"),
            metadata_filters=[],
            user_response_status_filter=None,
            offset=0,
            limit=5,
            sort_by=None,
            user_id=owner.id,
        )
        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json["items"]) == 2
        assert response_json["total"] == 2

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_search_current_user_dataset_records_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        workspace_a = await WorkspaceFactory.create()
        workspace_b = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace_a], role=role)
        dataset, *_ = await self.create_dataset_with_user_responses(user, workspace_b)

        query_json = {"query": {"text": {"q": "unit test", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json=query_json,
        )

        assert response.status_code == 403

    async def test_search_current_user_dataset_records_with_non_existent_field(
        self, async_client: "AsyncClient", owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, *_ = await self.create_dataset_with_user_responses(owner, workspace)

        query_json = {"query": {"text": {"q": "unit test", "field": "i do not exist"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{dataset.id}/records/search", headers=owner_auth_header, json=query_json
        )

        assert response.status_code == 422

    async def test_search_current_user_dataset_records_with_non_existent_dataset(
        self, async_client: "AsyncClient", owner_auth_header
    ):
        query_json = {"query": {"text": {"q": "unit test", "field": "input"}}}
        response = await async_client.post(
            f"/api/v1/me/datasets/{uuid4()}/records/search", headers=owner_auth_header, json=query_json
        )

        assert response.status_code == 404, response.json()

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

        test_telemetry.track_data.assert_called_once_with(action="PublishedDataset", data={"questions": ["rating"]})
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
            {"name": "New Name", "guidelines": "New Guidelines", "allow_extra_metadata": False},
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
        allow_extra_metadata = payload.get("allow_extra_metadata") or dataset.allow_extra_metadata

        assert response.status_code == 200
        response_body = response.json()
        assert response_body == {
            "id": str(dataset.id),
            "name": name,
            "guidelines": guidelines,
            "allow_extra_metadata": allow_extra_metadata,
            "status": "ready",
            "workspace_id": str(dataset.workspace_id),
            "last_activity_at": dataset.last_activity_at.isoformat(),
            "inserted_at": dataset.inserted_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
        }
        assert response_body["last_activity_at"] == response_body["updated_at"]

        assert dataset.name == name
        assert dataset.guidelines == guidelines
        assert dataset.allow_extra_metadata is allow_extra_metadata

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
            {"allow_extra_metadata": None},
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

    async def create_dataset_with_user_responses(
        self, user: User, workspace: "Workspace"
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
            await RecordFactory.create(fields={"input": "input_c", "output": "output_c"}, dataset=dataset),
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

    async def test_get_record_with_response_for_deleted_user(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: "SearchEngine",
        owner: User,
        owner_auth_header: dict,
    ):
        record = await RecordFactory.create()
        user = await OwnerFactory.create()
        response = await ResponseFactory.create(record=record, user=user)

        mock_search_engine.search.return_value = SearchResponses(
            items=[SearchResponseItem(record_id=record.id)], total=1
        )

        await db.delete(user)

        http_response = await async_client.get(
            f"/api/v1/datasets/{record.dataset.id}/records",
            params={"include": ["responses"]},
            headers=owner_auth_header,
        )

        response_json = http_response.json()
        assert http_response.status_code == 200

        response_items = response_json["items"]
        assert len(response_items) == 1
        assert response_items[0]["id"] == str(record.id)
        assert response_items[0]["responses"][0]["id"] == str(response.id)
        assert response_items[0]["responses"][0]["user_id"] is None
