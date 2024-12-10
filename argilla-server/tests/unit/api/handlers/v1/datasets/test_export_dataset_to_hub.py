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
from rq.job import JobStatus
from httpx import AsyncClient

from argilla_server.jobs.queues import DEFAULT_QUEUE
from argilla_server.constants import API_KEY_HEADER_NAME

from tests.factories import AdminFactory, DatasetFactory, AnnotatorFactory, RecordFactory


@pytest.mark.asyncio
class TestExportDatasetToHub:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/export"

    async def test_export_dataset_to_hub(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "hf-username/dataset-name",
                "token": "hf-secret-token",
            },
        )

        assert response.status_code == 202

        response_json = response.json()
        assert response_json["id"]
        assert response_json["status"] == JobStatus.QUEUED

        assert DEFAULT_QUEUE.count == 1
        assert DEFAULT_QUEUE.jobs[0].kwargs == {
            "name": "hf-username/dataset-name",
            "subset": "default",
            "split": "train",
            "private": False,
            "token": "hf-secret-token",
            "dataset_id": dataset.id,
        }

    async def test_export_dataset_to_hub_with_non_default_values(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(dataset=dataset)

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "hf-username/dataset-name",
                "subset": "hf-subset",
                "split": "hf-split",
                "private": True,
                "token": "hf-secret-token",
            },
        )

        assert response.status_code == 202

        response_json = response.json()
        assert response_json["id"]
        assert response_json["status"] == JobStatus.QUEUED

        assert DEFAULT_QUEUE.count == 1
        assert DEFAULT_QUEUE.jobs[0].kwargs == {
            "name": "hf-username/dataset-name",
            "subset": "hf-subset",
            "split": "hf-split",
            "private": True,
            "token": "hf-secret-token",
            "dataset_id": dataset.id,
        }

    async def test_export_dataset_to_hub_as_admin(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(dataset=dataset)

        admin = await AdminFactory.create(workspaces=[dataset.workspace])

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json={
                "name": "username/dataset-name",
                "token": "secret-hf-token",
            },
        )

        assert response.status_code == 202

        assert DEFAULT_QUEUE.count == 1

    async def test_export_dataset_to_hub_as_admin_from_different_workspace(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        admin = await AdminFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json={
                "name": "username/dataset-name",
                "token": "secret-hf-token",
            },
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ForbiddenOperationError",
                "params": {"detail": "Operation not allowed"},
            },
        }

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_to_hub_as_annotator(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={
                "name": "username/dataset-name",
                "token": "secret-hf-token",
            },
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ForbiddenOperationError",
                "params": {"detail": "Operation not allowed"},
            },
        }

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_to_hub_without_authentication(self, async_client: AsyncClient):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            json={
                "name": "username/dataset-name",
                "token": "secret-hf-token",
            },
        )

        assert response.status_code == 401
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::UnauthorizedError",
                "params": {
                    "detail": "Could not validate credentials",
                },
            },
        }

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_to_hub_with_nonexistent_dataset_id(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        await DatasetFactory.create()

        nonexistent_dataset_id = uuid4()

        response = await async_client.post(
            self.url(nonexistent_dataset_id),
            headers=owner_auth_header,
            json={
                "name": "username/dataset-name",
                "token": "secret-hf-token",
            },
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Dataset with id `{nonexistent_dataset_id}` not found"}

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_with_empty_name(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "",
                "token": "hf-secret-token",
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body", "name"],
                            "msg": "String should have at least 1 character",
                            "type": "string_too_short",
                        },
                    ],
                },
            },
        }

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_with_empty_subset(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "hf-username/dataset-name",
                "subset": "",
                "token": "hf-secret-token",
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body", "subset"],
                            "msg": "String should have at least 1 character",
                            "type": "string_too_short",
                        },
                    ],
                },
            },
        }

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_with_empty_split(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "hf-username/dataset-name",
                "split": "",
                "token": "hf-secret-token",
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body", "split"],
                            "msg": "String should have at least 1 character",
                            "type": "string_too_short",
                        },
                    ],
                },
            },
        }

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_with_empty_token(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "hf-username/dataset-name",
                "token": "",
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "errors": [
                        {
                            "loc": ["body", "token"],
                            "msg": "String should have at least 1 character",
                            "type": "string_too_short",
                        },
                    ],
                },
            },
        }

        assert DEFAULT_QUEUE.count == 0

    async def test_export_dataset_without_records(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        await RecordFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "hf-username/dataset-name",
                "token": "hf-secret-token",
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": f"Dataset with id `{dataset.id}` has no records to export"}

        assert DEFAULT_QUEUE.count == 0
