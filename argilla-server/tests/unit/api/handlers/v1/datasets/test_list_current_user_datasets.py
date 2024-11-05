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
from datetime import timedelta

from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import DatasetStatus, UserRole
from tests.factories import DatasetFactory, WorkspaceUserFactory, WorkspaceFactory, UserFactory


@pytest.mark.asyncio
class TestListCurrentUserDatasets:
    def url(self) -> str:
        return "/api/v1/me/datasets"

    async def test_list_current_user_datasets_sorted_by_inserted_at(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        another_dataset = await DatasetFactory.create(inserted_at=dataset.inserted_at + timedelta(seconds=10))

        response = await async_client.get(self.url(), headers=owner_auth_header)

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 2
        assert datasets[0]["id"] == str(dataset.id)
        assert datasets[1]["id"] == str(another_dataset.id)

    async def test_list_current_user_datasets_by_name(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create(name="dataset-a")
        await DatasetFactory.create(name="dataset-b")

        response = await async_client.get(
            self.url(),
            headers=owner_auth_header,
            params={"name": "dataset-a"},
        )

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)

    async def test_list_current_user_datasets_by_status(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create(status=DatasetStatus.draft)
        await DatasetFactory.create(status=DatasetStatus.ready)

        response = await async_client.get(
            self.url(),
            headers=owner_auth_header,
            params={"status": "draft"},
        )

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)

    async def test_list_current_user_datasets_by_workspace_id(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        await DatasetFactory.create()

        response = await async_client.get(
            self.url(),
            headers=owner_auth_header,
            params={"workspace_id": str(dataset.workspace_id)},
        )

        assert response.status_code == 200, response.json()
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)

    async def test_list_current_user_datasets_by_status_and_name(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(name="a-dataset", status=DatasetStatus.draft)
        await DatasetFactory.create(status=DatasetStatus.draft)
        await DatasetFactory.create(status=DatasetStatus.ready)

        response = await async_client.get(
            self.url(),
            headers=owner_auth_header,
            params={"status": "draft", "name": "a-dataset"},
        )

        assert response.status_code == 200
        response_json = response.json()

        datasets = response_json["items"]
        assert len(datasets) == 1
        assert datasets[0]["id"] == str(dataset.id)

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_list_current_user_datasets_as_restricted_user(self, async_client: AsyncClient, role: UserRole):
        workspace = await WorkspaceFactory.create()
        another_workspace = await WorkspaceFactory.create()

        dataset_a = await DatasetFactory.create(name="dataset-a", workspace=workspace)
        dataset_b = await DatasetFactory.create(name="dataset-b", workspace=workspace)
        dataset_c = await DatasetFactory.create(name="dataset-c", workspace=another_workspace)

        annotator = await UserFactory.create(role=role)
        another_annotator = await UserFactory.create(role=role)

        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=annotator.id)
        await WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=another_annotator.id)
        await WorkspaceUserFactory.create(workspace_id=another_workspace.id, user_id=another_annotator.id)

        response = await async_client.get(
            self.url(),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
        )

        assert response.status_code == 200

        assert [item["name"] for item in response.json()["items"]] == ["dataset-a", "dataset-b"]
