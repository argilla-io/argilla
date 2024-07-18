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

from uuid import UUID

import pytest

from httpx import AsyncClient

from argilla_server.models import User
from argilla_server.enums import DatasetDistributionStrategy, RecordStatus, ResponseStatus

from tests.factories import DatasetFactory, RecordFactory, ResponseFactory, TextQuestionFactory


@pytest.mark.asyncio
class TestDeleteResponse:
    def url(self, response_id: UUID) -> str:
        return f"/api/v1/responses/{response_id}"

    async def test_delete_response_updates_record_status_to_pending(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 1,
            }
        )

        record = await RecordFactory.create(status=RecordStatus.completed, dataset=dataset)
        response = await ResponseFactory.create(record=record)

        resp = await async_client.delete(self.url(response.id), headers=owner_auth_header)

        assert resp.status_code == 200
        assert record.status == RecordStatus.pending

    async def test_delete_response_does_not_updates_record_status_to_pending(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(
            distribution={
                "strategy": DatasetDistributionStrategy.overlap,
                "min_submitted": 2,
            }
        )

        record = await RecordFactory.create(status=RecordStatus.completed, dataset=dataset)
        responses = await ResponseFactory.create_batch(3, record=record)

        resp = await async_client.delete(self.url(responses[0].id), headers=owner_auth_header)

        assert resp.status_code == 200
        assert record.status == RecordStatus.completed
