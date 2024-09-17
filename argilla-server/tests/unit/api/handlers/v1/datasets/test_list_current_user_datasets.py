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
import uuid

import pytest
from httpx import AsyncClient
from pydantic.schema import timedelta

from argilla_server.enums import DatasetStatus
from tests.factories import DatasetFactory


@pytest.mark.asyncio
class TestListCurrentUserDatasets:
    async def test_list_user_datasets_sorted_by_insterted_at(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        another_dataset = await DatasetFactory.create(inserted_at=dataset.inserted_at + timedelta(seconds=10))

        response = await async_client.get("/api/v1/me/datasets", headers=owner_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 2
        assert datasets[0]["id"] == str(dataset.id)
        assert datasets[1]["id"] == str(another_dataset.id)

    async def test_list_user_datasets_by_name(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create(name="dataset-a")
        await DatasetFactory.create(name="dataset-b")

        response = await async_client.get(
            "/api/v1/me/datasets", params={"name": "dataset-a"}, headers=owner_auth_header
        )

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)

    async def test_list_user_datasets_by_status(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create(status=DatasetStatus.draft)
        await DatasetFactory.create(status=DatasetStatus.ready)

        response = await async_client.get("/api/v1/me/datasets", params={"status": "draft"}, headers=owner_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)

    async def test_list_users_datasets_by_workspace_id(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        await DatasetFactory.create()

        response = await async_client.get(
            "/api/v1/me/datasets",
            params={"workspace_id": str(dataset.workspace_id)},
            headers=owner_auth_header,
        )

        assert response.status_code == 200, response.json()
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)

    async def test_list_user_datasets_by_status_and_name(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create(name="a-dataset", status=DatasetStatus.draft)
        await DatasetFactory.create(status=DatasetStatus.draft)
        await DatasetFactory.create(status=DatasetStatus.ready)

        response = await async_client.get(
            "/api/v1/me/datasets", params={"status": "draft", "name": "a-dataset"}, headers=owner_auth_header
        )

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)
