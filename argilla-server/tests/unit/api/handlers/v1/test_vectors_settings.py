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
from argilla_server.api.schemas.v1.vector_settings import VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import UserRole

from tests.factories import AdminFactory, AnnotatorFactory, UserFactory, VectorSettingsFactory

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
class TestSuiteVectorsSettings:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_update_vector_settings(self, async_client: "AsyncClient", role: UserRole):
        vector_settings = await VectorSettingsFactory.create()
        user = await UserFactory.create(role=role, workspaces=[vector_settings.dataset.workspace])

        response = await async_client.patch(
            f"/api/v1/vectors-settings/{vector_settings.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"title": "New Title"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(vector_settings.id),
            "name": vector_settings.name,
            "title": "New Title",
            "dimensions": vector_settings.dimensions,
            "dataset_id": str(vector_settings.dataset_id),
            "inserted_at": vector_settings.inserted_at.isoformat(),
            "updated_at": vector_settings.updated_at.isoformat(),
        }

        assert vector_settings.title == "New Title"

    @pytest.mark.parametrize("title", [None, "", "t" * (VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH + 1)])
    async def test_update_vector_settings_with_invalid_title(
        self, async_client: "AsyncClient", owner_auth_header: dict, title: str
    ):
        vector_settings = await VectorSettingsFactory.create()

        response = await async_client.patch(
            f"/api/v1/vectors-settings/{vector_settings.id}",
            headers=owner_auth_header,
            json={"title": title},
        )

        assert response.status_code == 422

    async def test_update_vector_settings_with_title_as_none(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        vector_settings = await VectorSettingsFactory.create()

        response = await async_client.patch(
            f"/api/v1/vectors-settings/{vector_settings.id}",
            headers=owner_auth_header,
            json={"title": None},
        )

        assert response.status_code == 422

    async def test_update_vector_settings_non_existent(self, async_client: "AsyncClient", owner_auth_header: dict):
        vector_settings_id = uuid4()

        response = await async_client.patch(
            f"/api/v1/vectors-settings/{vector_settings_id}",
            headers=owner_auth_header,
            json={"title": "New Title"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"VectorSettings with id `{vector_settings_id}` not found"}

    async def test_update_vector_settings_as_admin_from_different_workspace(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        vector_settings = await VectorSettingsFactory.create()
        user = await AdminFactory.create()

        response = await async_client.patch(
            f"/api/v1/vectors-settings/{vector_settings.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"title": "New Title"},
        )

        assert response.status_code == 403

    async def test_update_vector_settings_as_annotator(self, async_client: "AsyncClient", owner_auth_header: dict):
        vector_settings = await VectorSettingsFactory.create()
        user = await UserFactory.create()

        response = await async_client.patch(
            f"/api/v1/vectors-settings/{vector_settings.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"title": "New Title"},
        )

        assert response.status_code == 403

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
            "title": vector_settings.title,
            "dimensions": vector_settings.dimensions,
            "dataset_id": str(vector_settings.dataset_id),
            "inserted_at": vector_settings.inserted_at.isoformat(),
            "updated_at": vector_settings.updated_at.isoformat(),
        }

    async def test_delete_vector_settings_non_existing(self, async_client: "AsyncClient", owner_auth_header: dict):
        vector_settings_id = uuid4()

        response = await async_client.delete(
            f"/api/v1/vectors-settings/{vector_settings_id}",
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"VectorSettings with id `{vector_settings_id}` not found"}

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
