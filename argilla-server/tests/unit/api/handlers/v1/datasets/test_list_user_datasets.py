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
from httpx import AsyncClient

from argilla_server.enums import DatasetStatus
from tests.factories import DatasetFactory


@pytest.mark.asyncio
class TestListUserDatasets:
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
