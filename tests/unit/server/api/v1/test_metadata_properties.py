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

from uuid import uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.enums import MetadataPropertyType
from argilla.server.models import MetadataProperty, UserRole
from sqlalchemy import func, select

from tests.factories import AnnotatorFactory, IntegerMetadataPropertyFactory, UserFactory


@pytest.mark.parametrize("user_role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete_metadata_property(async_client: "AsyncClient", db: "AsyncSession", user_role: UserRole):
    metadata_property = await IntegerMetadataPropertyFactory.create(
        name="name",
        description="description",
    )
    user = await UserFactory.create(role=user_role, workspaces=[metadata_property.dataset.workspace])

    response = await async_client.delete(
        f"/api/v1/metadata-properties/{metadata_property.id}", headers={API_KEY_HEADER_NAME: user.api_key}
    )

    assert response.status_code == 200
    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 0

    response_body = response.json()
    assert response_body == {
        "id": str(metadata_property.id),
        "name": "name",
        "description": "description",
        "settings": {"type": MetadataPropertyType.integer, "min": None, "max": None},
        "dataset_id": str(metadata_property.dataset_id),
        "inserted_at": metadata_property.inserted_at.isoformat(),
        "updated_at": metadata_property.updated_at.isoformat(),
    }


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
        f"/api/v1/metadata-properties/{metadata_property.id}", headers={API_KEY_HEADER_NAME: admin.api_key}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_metadata_property_as_annotator(async_client: "AsyncClient", db: "AsyncSession"):
    annotator = await AnnotatorFactory.create()
    metadata_property = await IntegerMetadataPropertyFactory.create()

    response = await async_client.delete(
        f"/api/v1/metadata-properties/{metadata_property.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
    )

    assert response.status_code == 403
    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1


@pytest.mark.asyncio
async def test_delete_metadata_property_with_nonexistent_metadata_property_id(
    async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
):
    await IntegerMetadataPropertyFactory.create()

    response = await async_client.delete(f"/api/v1/metadata-properties/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert (await db.execute(select(func.count(MetadataProperty.id)))).scalar() == 1
