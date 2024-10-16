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
from uuid import UUID

import pytest

from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import DatasetStatus, RecordStatus
from argilla_server.models import Dataset, Record
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    AnnotatorFactory,
)


@pytest.mark.asyncio
class TestDatasetRecordsBulk:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_dataset(self, **kwargs) -> Dataset:
        dataset = await DatasetFactory.create(status=DatasetStatus.ready, **kwargs)

        await self._configure_dataset_fields(dataset)
        await self._configure_dataset_metadata_properties(dataset)

        return dataset

    @pytest.mark.parametrize(
        "record_create",
        [
            {
                "fields": {
                    "prompt": "Does exercise help reduce stress?",
                    "response": "Exercise can definitely help reduce stress.",
                },
                "metadata": {"terms_metadata": ["a", "b", "c"]},
            },
            {
                "fields": {
                    "prompt": "Does exercise help reduce stress?",
                    "response": "Exercise can definitely help reduce stress.",
                },
                "metadata": {"terms_metadata": "a"},
                "external_id": "external-id-1",
            },
            {
                "fields": {
                    "prompt": "Does exercise help reduce stress?",
                    "response": "Exercise can definitely help reduce stress.",
                },
                "external_id": "external-id-2",
            },
        ],
    )
    async def test_create_dataset_records_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict, record_create: dict
    ):
        dataset = await self.test_dataset()

        response = await async_client.post(
            self.url(dataset.id), headers=owner_auth_header, json={"items": [record_create]}
        )

        assert response.status_code == 201, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 1
        record = (await db.execute(select(Record))).scalar_one()

        response_json = response.json()
        assert response_json == {
            "items": [
                {
                    "id": str(record.id),
                    "status": RecordStatus.pending,
                    "dataset_id": str(dataset.id),
                    "external_id": record.external_id,
                    "fields": record.fields,
                    "metadata": record.metadata_,
                    "inserted_at": record.inserted_at.isoformat(),
                    "updated_at": record.updated_at.isoformat(),
                    "vectors": {},
                    "responses": [],
                    "suggestions": [],
                }
            ]
        }

    @pytest.mark.parametrize("metadata", [{"terms_metadata": "b"}, {"terms_metadata": ["c", "a"]}, {}, None])
    async def test_update_record_metadata_by_id(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict, metadata: dict
    ) -> None:
        dataset = await self.test_dataset()
        records = await RecordFactory.create_batch(dataset=dataset, size=10)

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={"items": [{"id": str(record.id), "metadata": metadata} for record in records]},
        )

        assert response.status_code == 200
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == len(records)
        updated_records = (await db.execute(select(Record))).scalars().all()
        for record in updated_records:
            assert record.metadata_ == metadata

    @pytest.mark.parametrize("metadata", [{"terms_metadata": "b"}, {"terms_metadata": ["c", "a"]}, {}, None])
    async def test_update_record_metadata_by_external_id(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict, metadata: dict
    ):
        dataset = await self.test_dataset()
        records = await RecordFactory.create_batch(dataset=dataset, size=10)

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [{"external_id": record.external_id, "metadata": metadata} for record in records],
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == len(records)
        updated_records = (await db.execute(select(Record))).scalars().all()
        for record in updated_records:
            assert record.metadata_ == metadata

    async def test_update_record_metadata_with_invalid_external_id_but_correct_id(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        records = await RecordFactory.create_batch(dataset=dataset, size=10)

        new_metadata = {"whatever": "whatever"}
        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {"id": str(record.id), "external_id": str(uuid.uuid4()), "metadata": new_metadata}
                    for record in records
                ],
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == len(records)
        updated_records = (await db.execute(select(Record))).scalars().all()
        for record in updated_records:
            assert record.metadata_ == new_metadata

    async def test_upsert_record_for_other_dataset(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        other_dataset = await self.test_dataset()

        record = await RecordFactory.create(dataset=dataset)
        response = await async_client.put(
            self.url(other_dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {"id": str(record.id), "metadata": {"terms_metadata": "b"}},
                ],
            },
        )

        assert response.status_code == 422  # The insert is failing because no fields are provided
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 1
        assert (await db.execute(select(Record))).scalar_one().metadata_ is None

    async def test_create_records_in_bulk_as_annotator(self, async_client: AsyncClient):
        user = await AnnotatorFactory.create()

        dataset = await self.test_dataset()

        response = await async_client.post(
            self.url(dataset.id),
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"items": [{"fields": {"text": "The text field"}}]},
        )

        assert response.status_code == 403, response.json()

    async def _configure_dataset_metadata_properties(self, dataset):
        await TermsMetadataPropertyFactory.create(name="terms_metadata", dataset=dataset)

        await dataset.awaitable_attrs.metadata_properties

    async def _configure_dataset_fields(self, dataset):
        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextFieldFactory.create(name="response", dataset=dataset)

        await dataset.awaitable_attrs.fields
