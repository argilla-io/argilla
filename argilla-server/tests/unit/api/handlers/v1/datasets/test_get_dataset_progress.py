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

from uuid import UUID, uuid4

import pytest
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import ResponseStatus, UserRole
from httpx import AsyncClient

from tests.factories import DatasetFactory, RecordFactory, ResponseFactory, UserFactory


@pytest.mark.asyncio
class TestGetDatasetProgress:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/progress"

    async def test_get_dataset_progress(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        record_with_one_submitted_response = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create(record=record_with_one_submitted_response)

        record_with_multiple_submitted_responses = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create_batch(3, record=record_with_multiple_submitted_responses)

        record_with_one_draft_response = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create(record=record_with_one_draft_response, status=ResponseStatus.draft)

        record_with_multiple_draft_responses = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create_batch(3, record=record_with_multiple_draft_responses, status=ResponseStatus.draft)

        record_with_one_discarded_response = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create(record=record_with_one_discarded_response, status=ResponseStatus.discarded)

        record_with_multiple_discarded_responses = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create_batch(
            3, record=record_with_multiple_discarded_responses, status=ResponseStatus.discarded
        )

        record_with_mixed_responses = await RecordFactory.create(dataset=dataset)
        await ResponseFactory.create(record=record_with_mixed_responses)
        await ResponseFactory.create(record=record_with_mixed_responses, status=ResponseStatus.draft)
        await ResponseFactory.create(record=record_with_mixed_responses, status=ResponseStatus.discarded)

        record_without_responses = await RecordFactory.create(dataset=dataset)

        other_dataset = await DatasetFactory.create()

        other_record_with_one_submitted_response = await RecordFactory.create(dataset=other_dataset)
        await ResponseFactory.create(record=other_record_with_one_submitted_response)

        other_record_with_multiple_submitted_responses = await RecordFactory.create(dataset=other_dataset)
        await ResponseFactory.create_batch(3, record=other_record_with_multiple_submitted_responses)

        other_record_with_one_draft_response = await RecordFactory.create(dataset=other_dataset)
        await ResponseFactory.create(record=other_record_with_one_draft_response, status=ResponseStatus.draft)

        other_record_with_multiple_draft_responses = await RecordFactory.create(dataset=other_dataset)
        await ResponseFactory.create_batch(
            3, record=other_record_with_multiple_draft_responses, status=ResponseStatus.draft
        )

        other_record_with_one_discarded_response = await RecordFactory.create(dataset=other_dataset)
        await ResponseFactory.create(record=other_record_with_one_discarded_response, status=ResponseStatus.discarded)

        other_record_with_multiple_discarded_responses = await RecordFactory.create(dataset=other_dataset)
        await ResponseFactory.create_batch(
            3, record=other_record_with_multiple_discarded_responses, status=ResponseStatus.discarded
        )

        other_record_with_mixed_responses = await RecordFactory.create(dataset=other_dataset)
        await ResponseFactory.create(record=other_record_with_mixed_responses)
        await ResponseFactory.create(record=other_record_with_mixed_responses, status=ResponseStatus.draft)
        await ResponseFactory.create(record=other_record_with_mixed_responses, status=ResponseStatus.discarded)

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "total": 8,
            "submitted": 2,
            "discarded": 2,
            "conflicting": 1,
            "pending": 3,
        }

    async def test_get_dataset_progress_with_empty_dataset(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "total": 0,
            "submitted": 0,
            "discarded": 0,
            "conflicting": 0,
            "pending": 0,
        }

    @pytest.mark.parametrize("user_role", [UserRole.admin, UserRole.annotator])
    async def test_get_dataset_progress_as_restricted_user(self, async_client: AsyncClient, user_role: UserRole):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=user_role)

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
