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

from typing import TYPE_CHECKING, Type
from uuid import uuid4

import pytest
from argilla_server.api.schemas.v1.metadata_properties import METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import MetadataPropertyType, UserRole
from argilla_server.models import MetadataProperty, UserRole
from argilla_server.search_engine import FloatMetadataMetrics, IntegerMetadataMetrics, TermsMetadataMetrics
from sqlalchemy import func, select

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    BaseFactory,
    FloatMetadataPropertyFactory,
    IntegerMetadataPropertyFactory,
    TermsMetadataPropertyFactory,
    UserFactory,
    WorkspaceUserFactory,
)

if TYPE_CHECKING:
    from argilla_server.search_engine import MetadataMetrics, SearchEngine
    from httpx import AsyncClient


@pytest.mark.asyncio
class TestSuiteMetadataProperties:
    @pytest.mark.parametrize(
        ("factory_class", "expected_metric", "expected_json"),
        [
            (
                TermsMetadataPropertyFactory,
                TermsMetadataMetrics(total=10, values=[TermsMetadataMetrics.TermCount(term="term", count=10)]),
                {"type": "terms", "total": 10, "values": [{"term": "term", "count": 10}]},
            ),
            (
                IntegerMetadataPropertyFactory,
                IntegerMetadataMetrics(min=10, max=100),
                {"type": "integer", "min": 10, "max": 100},
            ),
            (
                FloatMetadataPropertyFactory,
                FloatMetadataMetrics(min=10.3, max=11.32),
                {"type": "float", "min": 10.3, "max": 11.32},
            ),
            (
                FloatMetadataPropertyFactory,
                FloatMetadataMetrics(min=1.23456789, max=2.34567890),
                {"type": "float", "min": 1.23457, "max": 2.34568},
            ),
        ],
    )
    async def test_get_metadata_property_metrics(
        self,
        async_client: "AsyncClient",
        mock_search_engine: "SearchEngine",
        owner_auth_header: dict,
        factory_class: Type[BaseFactory],
        expected_metric: "MetadataMetrics",
        expected_json: dict,
    ):
        metadata_property = await factory_class.create()

        mock_search_engine.compute_metrics_for.return_value = expected_metric

        response = await async_client.get(
            f"/api/v1/metadata-properties/{metadata_property.id}/metrics", headers=owner_auth_header
        )

        assert response.status_code == 200
        assert response.json() == expected_json

    async def test_get_metadata_property_metrics_without_authentication(self, async_client: "AsyncClient"):
        metadata_property = await TermsMetadataPropertyFactory.create()

        response = await async_client.get(f"/api/v1/metadata-properties/{metadata_property.id}/metrics")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_get_metadata_property_metrics_as_allowed_role(
        self, async_client: "AsyncClient", mock_search_engine: "SearchEngine", role: UserRole
    ):
        metadata_property = await IntegerMetadataPropertyFactory.create(allowed_roles=[role])
        workspace = metadata_property.dataset.workspace

        user = await UserFactory.create(role=role)

        await WorkspaceUserFactory.create(user_id=user.id, workspace_id=workspace.id)

        mock_search_engine.compute_metrics_for.return_value = IntegerMetadataMetrics(min=0, max=10)

        response = await async_client.get(
            f"/api/v1/metadata-properties/{metadata_property.id}/metrics", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_get_metadata_property_metrics_as_non_allowed_role(
        self, async_client: "AsyncClient", mock_search_engine: "SearchEngine", role: UserRole
    ):
        metadata_property = await IntegerMetadataPropertyFactory.create(allowed_roles=[])
        workspace = metadata_property.dataset.workspace

        user = await UserFactory.create(role=role)

        await WorkspaceUserFactory.create(user_id=user.id, workspace_id=workspace.id)

        mock_search_engine.compute_metrics_for.return_value = IntegerMetadataMetrics(min=0, max=10)

        response = await async_client.get(
            f"/api/v1/metadata-properties/{metadata_property.id}/metrics", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403

    async def test_get_metadata_property_metrics_with_nonexistent_metadata_property(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        metadata_property_id = uuid4()

        await TermsMetadataPropertyFactory.create()

        response = await async_client.get(
            f"/api/v1/metadata-properties/{metadata_property_id}/metrics",
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"MetadataProperty with id `{metadata_property_id}` not found"}

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_get_metadata_property_metrics_as_restricted_user_role_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        user = await UserFactory.create(role=role)
        metadata_property = await TermsMetadataPropertyFactory.create()

        response = await async_client.get(
            f"/api/v1/metadata-properties/{metadata_property.id}/metrics", headers={API_KEY_HEADER_NAME: user.api_key}
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_metadata_property(async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict):
    metadata_property = await IntegerMetadataPropertyFactory.create(
        name="name", title="title", allowed_roles=[UserRole.admin, UserRole.annotator]
    )

    assert metadata_property.visible_for_annotators == True

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers=owner_auth_header,
        json={"title": "updated title", "visible_for_annotators": False},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(metadata_property.id),
        "name": "name",
        "title": "updated title",
        "settings": {"type": "integer", "min": None, "max": None},
        "visible_for_annotators": False,
        "dataset_id": str(metadata_property.dataset.id),
        "inserted_at": metadata_property.inserted_at.isoformat(),
        "updated_at": metadata_property.updated_at.isoformat(),
    }

    metadata_property = await db.get(MetadataProperty, metadata_property.id)
    assert metadata_property.title == "updated title"
    assert metadata_property.visible_for_annotators == False
    assert metadata_property.allowed_roles == [UserRole.admin]


@pytest.mark.asyncio
async def test_update_metadata_property_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    metadata_property = await IntegerMetadataPropertyFactory.create()

    response = await async_client.patch(f"/api/v1/metadata-properties/{metadata_property.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_metadata_property_title(async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict):
    metadata_property = await IntegerMetadataPropertyFactory.create(title="title")

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers=owner_auth_header,
        json={"title": "updated title"},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["title"] == "updated title"

    metadata_property = await db.get(MetadataProperty, metadata_property.id)
    assert metadata_property.title == "updated title"


@pytest.mark.parametrize(
    "title",
    [None, "", "t" * (METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH + 1)],
)
@pytest.mark.asyncio
async def test_update_metadata_property_with_invalid_title(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, title: str
):
    metadata_property = await IntegerMetadataPropertyFactory.create(title="title")

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers=owner_auth_header,
        json={"title": title},
    )

    assert response.status_code == 422

    metadata_property = await db.get(MetadataProperty, metadata_property.id)
    assert metadata_property.title == "title"


@pytest.mark.asyncio
async def test_update_metadata_property_enabling_visible_for_annotators(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    metadata_property = await IntegerMetadataPropertyFactory.create(allowed_roles=[UserRole.admin])

    assert metadata_property.visible_for_annotators == False

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers=owner_auth_header,
        json={"visible_for_annotators": True},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["visible_for_annotators"] == True

    metadata_property = await db.get(MetadataProperty, metadata_property.id)
    assert metadata_property.visible_for_annotators == True
    assert metadata_property.allowed_roles == [UserRole.admin, UserRole.annotator]


@pytest.mark.asyncio
async def test_update_metadata_property_disabling_visible_for_annotators(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    metadata_property = await IntegerMetadataPropertyFactory.create(allowed_roles=[UserRole.admin, UserRole.annotator])

    assert metadata_property.visible_for_annotators == True

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers=owner_auth_header,
        json={"visible_for_annotators": False},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["visible_for_annotators"] == False

    metadata_property = await db.get(MetadataProperty, metadata_property.id)
    assert metadata_property.visible_for_annotators == False
    assert metadata_property.allowed_roles == [UserRole.admin]


@pytest.mark.asyncio
async def test_update_metadata_property_with_visible_for_annotators_as_none(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    metadata_property = await IntegerMetadataPropertyFactory.create(allowed_roles=[UserRole.admin, UserRole.annotator])

    assert metadata_property.visible_for_annotators == True

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers=owner_auth_header,
        json={"visible_for_annotators": None},
    )

    assert response.status_code == 422

    metadata_property = await db.get(MetadataProperty, metadata_property.id)
    assert metadata_property.visible_for_annotators == True
    assert metadata_property.allowed_roles == [UserRole.admin, UserRole.annotator]


@pytest.mark.asyncio
async def test_update_metadata_property_as_admin(async_client: "AsyncClient", db: "AsyncSession"):
    metadata_property = await IntegerMetadataPropertyFactory.create()
    admin = await AdminFactory.create(workspaces=[metadata_property.dataset.workspace])

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers={API_KEY_HEADER_NAME: admin.api_key},
        json={},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_metadata_property_as_admin_from_different_workspace(
    async_client: "AsyncClient", db: "AsyncSession"
):
    metadata_property = await IntegerMetadataPropertyFactory.create()
    admin = await AdminFactory.create()

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers={API_KEY_HEADER_NAME: admin.api_key},
        json={},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_metadata_property_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    metadata_property = await IntegerMetadataPropertyFactory.create()
    annotator = await AnnotatorFactory.create(workspaces=[metadata_property.dataset.workspace])

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
        json={},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_metadata_property_with_empty_payload(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    metadata_property = await IntegerMetadataPropertyFactory.create()

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers=owner_auth_header,
        json={},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_metadata_property_with_nonexistent_metadata_property_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    metadata_property_id = uuid4()

    await IntegerMetadataPropertyFactory.create()

    response = await async_client.patch(
        f"/api/v1/metadata-properties/{metadata_property_id}",
        headers=owner_auth_header,
        json={},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"MetadataProperty with id `{metadata_property_id}` not found"}


@pytest.mark.parametrize("user_role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete_metadata_property(async_client: "AsyncClient", db: "AsyncSession", user_role: UserRole):
    metadata_property = await IntegerMetadataPropertyFactory.create(name="name", title="title")

    user = await UserFactory.create(role=user_role, workspaces=[metadata_property.dataset.workspace])

    response = await async_client.delete(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers={API_KEY_HEADER_NAME: user.api_key},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(metadata_property.id),
        "name": "name",
        "title": "title",
        "settings": {"type": MetadataPropertyType.integer, "min": None, "max": None},
        "visible_for_annotators": True,
        "dataset_id": str(metadata_property.dataset_id),
        "inserted_at": metadata_property.inserted_at.isoformat(),
        "updated_at": metadata_property.updated_at.isoformat(),
    }

    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 0


@pytest.mark.asyncio
async def test_delete_metadata_property_without_authentication(async_client: "AsyncClient", db: "AsyncSession"):
    metadata_property = await IntegerMetadataPropertyFactory.create()

    response = await async_client.delete(f"/api/v1/metadata-properties/{metadata_property.id}")

    assert response.status_code == 401
    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_metadata_property_as_admin_from_different_workspace(
    async_client: "AsyncClient", db: "AsyncSession"
):
    admin = await UserFactory.create(role=UserRole.admin)
    metadata_property = await IntegerMetadataPropertyFactory.create()

    response = await async_client.delete(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers={API_KEY_HEADER_NAME: admin.api_key},
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_metadata_property_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    metadata_property = await IntegerMetadataPropertyFactory.create()

    response = await async_client.delete(
        f"/api/v1/metadata-properties/{metadata_property.id}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_metadata_property_with_nonexistent_metadata_property_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    metadata_property_id = uuid4()

    await IntegerMetadataPropertyFactory.create()

    response = await async_client.delete(
        f"/api/v1/metadata-properties/{metadata_property_id}",
        headers=owner_auth_header,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"MetadataProperty with id `{metadata_property_id}` not found"}

    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1
