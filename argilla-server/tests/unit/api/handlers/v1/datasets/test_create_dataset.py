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

from typing import Any
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.enums import DatasetDistributionStrategy, DatasetStatus
from argilla_server.models import Dataset

from tests.factories import WorkspaceFactory


@pytest.mark.asyncio
class TestCreateDataset:
    def url(self) -> str:
        return "/api/v1/datasets"

    async def test_create_dataset_with_default_distribution(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "name": "Dataset Name",
                "workspace_id": str(workspace.id),
            },
        )

        dataset = (await db.execute(select(Dataset))).scalar_one()

        assert response.status_code == 201
        assert response.json() == {
            "id": str(dataset.id),
            "name": "Dataset Name",
            "guidelines": None,
            "allow_extra_metadata": True,
            "status": DatasetStatus.draft,
            "distribution": {
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            },
            "metadata": None,
            "workspace_id": str(workspace.id),
            "last_activity_at": dataset.last_activity_at.isoformat(),
            "inserted_at": dataset.inserted_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
        }

    async def test_create_dataset_with_overlap_distribution(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "name": "Dataset Name",
                "distribution": {
                    "strategy": DatasetDistributionStrategy.overlap,
                    "min_submitted": 4,
                },
                "workspace_id": str(workspace.id),
            },
        )

        dataset = (await db.execute(select(Dataset))).scalar_one()

        assert response.status_code == 201
        assert response.json() == {
            "id": str(dataset.id),
            "name": "Dataset Name",
            "guidelines": None,
            "allow_extra_metadata": True,
            "status": DatasetStatus.draft,
            "distribution": {
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 4,
            },
            "metadata": None,
            "workspace_id": str(workspace.id),
            "last_activity_at": dataset.last_activity_at.isoformat(),
            "inserted_at": dataset.inserted_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
        }

    async def test_create_dataset_with_overlap_distribution_using_invalid_min_submitted_value(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "name": "Dataset name",
                "distribution": {
                    "strategy": DatasetDistributionStrategy.overlap,
                    "min_submitted": 0,
                },
                "workspace_id": str(workspace.id),
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Dataset.id)))).scalar_one() == 0

    async def test_create_dataset_with_invalid_distribution_strategy(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "name": "Dataset Name",
                "distribution": {
                    "strategy": "invalid_strategy",
                },
                "workspace_id": str(workspace.id),
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Dataset.id)))).scalar_one() == 0

    async def test_create_dataset_with_default_metadata(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "name": "Dataset Name",
                "workspace_id": str(workspace.id),
            },
        )

        assert response.status_code == 201
        assert response.json()["metadata"] == None

        dataset = (await db.execute(select(Dataset))).scalar_one()
        assert dataset.metadata_ == None

    async def test_create_dataset_with_custom_metadata(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "name": "Dataset Name",
                "metadata": {"key": "value"},
                "workspace_id": str(workspace.id),
            },
        )

        assert response.status_code == 201
        assert response.json()["metadata"] == {"key": "value"}

        dataset = (await db.execute(select(Dataset))).scalar_one()
        assert dataset.metadata_ == {"key": "value"}

    @pytest.mark.parametrize("invalid_metadata", ["invalid_metadata", 123])
    async def test_create_dataset_with_invalid_metadata(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict, invalid_metadata: Any
    ):
        workspace = await WorkspaceFactory.create()

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "name": "Dataset Name",
                "metadata": invalid_metadata,
                "workspace_id": str(workspace.id),
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Dataset.id)))).scalar_one() == 0
