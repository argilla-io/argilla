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
from argilla_server.enums import DatasetStatus
from argilla_server.models import Dataset, Vector
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    RecordFactory,
    TextFieldFactory,
    VectorFactory,
    VectorSettingsFactory,
)


@pytest.mark.asyncio
class TestDatasetRecordsBulkWithVectors:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_dataset(self, **kwargs) -> Dataset:
        dataset = await DatasetFactory.create(status=DatasetStatus.ready, **kwargs)

        await self._configure_dataset_fields(dataset)
        await self._configure_dataset_vectors(dataset)

        return dataset

    async def test_create_record_with_vectors_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "vectors": {vector_settings.name: [1.0] * vector_settings.dimensions},
                    },
                ]
            },
        )

        assert response.status_code == 201, response.json()
        assert (await db.execute(select(func.count(Vector.id)))).scalar_one() == 1
        vector = (await db.execute(select(Vector))).scalar_one()

        response_json = response.json()
        for record in response_json["items"]:
            assert str(vector.record_id) == record["id"]
            assert vector.vector_settings_id == vector_settings.id
            assert record["vectors"] == {vector_settings.name: vector.value}

    async def test_update_records_with_new_vectors_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "vectors": {vector_settings.name: [1.0] * vector_settings.dimensions},
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Vector.id)))).scalar_one() == 1
        vector = (await db.execute(select(Vector))).scalar_one()

        response_json = response.json()
        records = response_json["items"]
        for record in records:
            assert str(vector.record_id) == record["id"]
            assert vector.vector_settings_id == vector_settings.id
            assert record["vectors"] == {vector_settings.name: vector.value}

    async def test_create_records_with_vectors_in_bulk_upsert(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "vectors": {vector_settings.name: [1.0] * vector_settings.dimensions},
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Vector.id)))).scalar_one() == 1
        vector = (await db.execute(select(Vector))).scalar_one()

        response_json = response.json()
        for record in response_json["items"]:
            assert str(vector.record_id) == record["id"]
            assert vector.vector_settings_id == vector_settings.id
            assert record["vectors"] == {vector_settings.name: vector.value}

    async def test_update_record_vectors_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        await VectorFactory.create(
            record=record, vector_settings=vector_settings, value=[0.5] * vector_settings.dimensions
        )

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "vectors": {vector_settings.name: [0.1] * vector_settings.dimensions},
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Vector.id)))).scalar_one() == 1
        vector = (await db.execute(select(Vector))).scalar_one()

        records = response.json()["items"]
        assert len(records) == 1
        for record in records:
            assert str(vector.record_id) == record["id"]
            assert vector.vector_settings_id == vector_settings.id
            assert record["vectors"] == {vector_settings.name: vector.value}

    async def test_update_record_with_vectors_with_new_vectors_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")
        other_vector_settings = dataset.vector_settings_by_name("response_embeddings")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        vector = await VectorFactory.create(
            record=record, vector_settings=vector_settings, value=[0.5] * vector_settings.dimensions
        )

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "vectors": {other_vector_settings.name: [0.1] * other_vector_settings.dimensions},
                    },
                ]
            },
        )

        assert response.status_code == 200, response.json()
        assert (await db.execute(select(func.count(Vector.id)))).scalar_one() == 2
        other_vector = (
            await db.execute(select(Vector).filter(Vector.vector_settings_id == other_vector_settings.id))
        ).scalar_one()

        records = response.json()["items"]
        assert len(records) == 1
        for record in records:
            assert record["vectors"] == {
                vector_settings.name: vector.value,
                other_vector_settings.name: other_vector.value,
            }

    async def test_create_record_with_wrong_vector_name_in_bulk(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "vectors": {"wrong_name": [1.0] * 10},
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": "Record at position 0 is not valid because record does not have valid vectors: "
            f"vector with name=wrong_name does not exist for dataset_id={dataset.id}"
        }

    async def test_create_record_with_wrong_vector_value_in_bulk(
        self, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "fields": {
                            "prompt": "Does exercise help reduce stress?",
                            "response": "Exercise can definitely help reduce stress.",
                        },
                        "vectors": {vector_settings.name: [1.0] * 5},
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": f"Record at position 0 is not valid because record does not have valid vectors: vector value for "
            f"vector name={vector_settings.name} must have 10 elements, got 5 elements"
        }

    async def test_update_record_with_wrong_vector_name_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        await VectorFactory.create(
            record=record, vector_settings=vector_settings, value=[1.0] * vector_settings.dimensions
        )
        other_vector_settings = await VectorSettingsFactory.create(name="other_vector_settings")

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "vectors": {other_vector_settings.name: [1.0] * other_vector_settings.dimensions},
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": f"Record at position 0 is not valid because record does not have valid vectors: vector with name={other_vector_settings.name} "
            f"does not exist for dataset_id={dataset.id}"
        }

    async def test_update_record_with_wrong_vector_value_in_bulk(
        self, async_client: AsyncClient, db: AsyncSession, owner_auth_header: dict
    ):
        dataset = await self.test_dataset()
        vector_settings = dataset.vector_settings_by_name("prompt_embeddings")
        record = await RecordFactory.create(dataset=dataset, fields={"prompt": "Does exercise help reduce stress?"})
        await VectorFactory.create(
            record=record, vector_settings=vector_settings, value=[1.0] * vector_settings.dimensions
        )

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "vectors": {vector_settings.name: [1.0] * 5},
                    },
                ]
            },
        )

        assert response.status_code == 422, response.json()
        assert response.json() == {
            "detail": f"Record at position 0 is not valid because record does not have valid vectors: vector value for "
            f"vector name={vector_settings.name} must have 10 elements, got 5 elements"
        }

    async def _configure_dataset_fields(self, dataset: Dataset) -> None:
        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextFieldFactory.create(name="response", dataset=dataset)

        await dataset.awaitable_attrs.fields

    async def _configure_dataset_vectors(self, dataset: Dataset) -> None:
        await VectorSettingsFactory.create(dataset=dataset, name="prompt_embeddings", dimensions=10)
        await VectorSettingsFactory.create(dataset=dataset, name="response_embeddings", dimensions=10)

        await dataset.awaitable_attrs.vectors_settings
