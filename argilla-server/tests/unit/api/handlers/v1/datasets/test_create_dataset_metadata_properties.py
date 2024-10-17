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
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID

import pytest
from sqlalchemy import func, select

from argilla_server.api.schemas.v1.metadata_properties import (
    METADATA_PROPERTY_CREATE_NAME_MAX_LENGTH,
    METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH,
    TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS,
)
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import (
    DatasetStatus,
)
from argilla_server.models import (
    Field,
    MetadataProperty,
    Question,
    UserRole,
)
from argilla_server.search_engine import (
    SearchEngine,
)
from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    TermsMetadataPropertyFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestCreateDatasetMetadataProperties:
    @pytest.mark.parametrize(
        ("settings", "expected_settings"),
        [
            ({"type": "terms"}, {"type": "terms", "values": None}),
            ({"type": "terms", "values": ["a"]}, {"type": "terms", "values": ["a"]}),
            ({"type": "terms", "values": [1, 2, 3]}, {"type": "terms", "values": [1, 2, 3]}),
            ({"type": "terms", "values": [True, False]}, {"type": "terms", "values": [True, False]}),
            ({"type": "terms", "values": [0.0, 0.5, 1.0]}, {"type": "terms", "values": [0.0, 0.5, 1.0]}),
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
            {"type": "terms", "values": -1},
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

        response = await async_client.post(
            f"/api/v1/datasets/{metadata_property.dataset_id}/metadata-properties",
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "settings": {"type": "terms", "values": ["a", "b", "c"]},
            },
        )

        assert response.status_code == 409
        assert response.json() == {
            "detail": f"Metadata property with name `{metadata_property.name}` already exists for dataset with id `{metadata_property.dataset_id}`"
        }

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
