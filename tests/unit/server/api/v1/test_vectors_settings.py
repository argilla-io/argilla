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

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.enums import UserRole

from tests.factories import AdminFactory, AnnotatorFactory, UserFactory, VectorSettingsFactory

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
class TestSuiteVectorsSettings:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_vector_settings(self, async_client: "AsyncClient", role: UserRole):
        vector_settings = await VectorSettingsFactory.create()
        user = await UserFactory.create(role=role, workspaces=[vector_settings.dataset.workspace])

        response = await async_client.delete(
            f"/api/v1/vectors-settings/{vector_settings.id}", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(vector_settings.id),
            "name": vector_settings.name,
            "dimensions": vector_settings.dimensions,
            "description": None,
            "inserted_at": vector_settings.inserted_at.isoformat(),
            "updated_at": vector_settings.updated_at.isoformat(),
        }

    async def test_delete_vector_settings_non_existing(self, async_client: "AsyncClient", owner_auth_header: dict):
        response = await async_client.delete(f"/api/v1/vectors-settings/{uuid4()}", headers=owner_auth_header)

        assert response.status_code == 404

    async def test_delete_vector_settings_as_annotator(self, async_client: "AsyncClient"):
        vector_settings = await VectorSettingsFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[vector_settings.dataset.workspace])

        response = await async_client.delete(
            f"/api/v1/vectors-settings/{vector_settings.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )

        assert response.status_code == 403

    async def test_delete_vector_settings_as_admin_from_another_workspace(self, async_client: "AsyncClient"):
        vector_settings = await VectorSettingsFactory.create()
        admin = await AdminFactory.create()

        response = await async_client.delete(
            f"/api/v1/vectors-settings/{vector_settings.id}", headers={API_KEY_HEADER_NAME: admin.api_key}
        )

        assert response.status_code == 403

    async def test_delete_vector_settings_without_authentication(self, async_client: "AsyncClient"):
        vector_settings = await VectorSettingsFactory.create()

        response = await async_client.delete(f"/api/v1/vectors-settings/{vector_settings.id}")

        assert response.status_code == 401
