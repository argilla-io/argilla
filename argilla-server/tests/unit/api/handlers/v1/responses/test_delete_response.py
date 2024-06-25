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

from argilla_server.enums import ResponseStatus

from tests.factories import RecordFactory, ResponseFactory


@pytest.mark.asyncio
class TestDeleteResponse:
    def url(self, response_id: UUID) -> str:
        return f"/api/v1/responses/{response_id}"

    async def test_delete_submitted_response_decreases_record_count_submitted_responses(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        record = await RecordFactory.create(count_submitted_responses=1)
        response = await ResponseFactory.create(status=ResponseStatus.submitted, record=record)

        resp = await async_client.delete(self.url(response.id), headers=owner_auth_header)

        assert resp.status_code == 200
        assert response.record.count_submitted_responses == 0

    @pytest.mark.parametrize("response_status", [ResponseStatus.draft, ResponseStatus.discarded])
    async def test_delete_not_submitted_response_does_not_modify_record_count_submitted_responses(
        self, async_client: AsyncClient, owner_auth_header: dict, response_status: ResponseStatus
    ):
        response = await ResponseFactory.create(status=response_status)

        resp = await async_client.delete(self.url(response.id), headers=owner_auth_header)

        assert resp.status_code == 200
        assert response.record.count_submitted_responses == 0
