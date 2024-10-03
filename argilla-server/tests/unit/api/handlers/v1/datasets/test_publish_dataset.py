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

from uuid import UUID
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import Record
from argilla_server.enums import DatasetStatus

from tests.factories import DatasetFactory, RecordFactory, FieldFactory, TextQuestionFactory


@pytest.mark.asyncio
class TestPublishDataset:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/publish"

    async def test_publish_draft_dataset_with_records_delete_all_records_before_publishing(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.draft)
        await FieldFactory.create(dataset=dataset)
        await TextQuestionFactory.create(required=True, dataset=dataset)

        records = await RecordFactory.create_batch(10, dataset=dataset)
        other_records = await RecordFactory.create_batch(4)

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == len(other_records)
