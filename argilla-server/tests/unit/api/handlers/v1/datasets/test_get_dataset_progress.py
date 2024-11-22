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

import pytest

from uuid import UUID, uuid4
from httpx import AsyncClient

from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import UserRole, RecordStatus
from argilla_server.search_engine import SearchEngine

from tests.factories import DatasetFactory, RecordFactory, UserFactory, DatasetUserFactory
from tests.unit.conftest import annotator


@pytest.mark.asyncio
class TestGetDatasetProgress:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/progress"

    async def test_get_dataset_progress(
        self, async_client: AsyncClient, mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        users = await UserFactory.create_batch(100)

        for user in users:
            await DatasetUserFactory.create(dataset_id=dataset.id, user_id=user.id)

        mock_search_engine.get_dataset_progress.return_value = {
            "total": 5,
            "completed": 3,
            "pending": 2,
        }

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200, response.json()
        assert response.json() == {
            "completed": 3,
            "pending": 2,
            "total": 5,
            "users": [{"username": user.username} for user in users],
        }

    async def test_get_dataset_progress_with_empty_dataset(
        self,
        async_client: AsyncClient,
        mock_search_engine: SearchEngine,
        owner_auth_header: dict,
    ):
        dataset = await DatasetFactory.create()

        mock_search_engine.get_dataset_progress.return_value = {}

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "completed": 0,
            "pending": 0,
            "total": 0,
            "users": [],
        }

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_get_dataset_progress_as_restricted_user(
        self,
        async_client: AsyncClient,
        mock_search_engine: SearchEngine,
        user_role: UserRole,
    ):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=user_role)

        mock_search_engine.get_dataset_progress.return_value = {}

        response = await async_client.get(self.url(dataset.id), headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 200

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_get_dataset_progress_as_restricted_user_from_different_workspace(
        self, async_client: AsyncClient, user_role: UserRole
    ):
        dataset = await DatasetFactory.create()

        other_dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[other_dataset.workspace], role=user_role)

        response = await async_client.get(self.url(dataset.id), headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 403
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ForbiddenOperationError",
                "params": {"detail": "Operation not allowed"},
            },
        }

    async def test_get_dataset_progress_without_authentication(self, async_client: AsyncClient):
        response = await async_client.get(self.url(uuid4()))

        assert response.status_code == 401
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::UnauthorizedError",
                "params": {"detail": "Could not validate credentials"},
            },
        }

    async def test_get_dataset_progress_with_nonexistent_dataset_id(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset_id = uuid4()

        response = await async_client.get(self.url(dataset_id), headers=owner_auth_header)

        assert response.status_code == 404
        assert response.json() == {"detail": f"Dataset with id `{dataset_id}` not found"}
