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

from argilla_server.enums import FieldType

from tests.factories import DatasetFactory, ImageFieldFactory


@pytest.mark.asyncio
class TestListDatasetFields:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/fields"

    async def test_list_dataset_fields_with_image_field(self, async_client: AsyncClient, owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        image_field_a = await ImageFieldFactory.create(dataset=dataset)
        image_field_b = await ImageFieldFactory.create(dataset=dataset)

        response = await async_client.get(self.url(dataset.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(image_field_a.id),
                    "name": image_field_a.name,
                    "title": image_field_a.title,
                    "required": False,
                    "settings": {"type": FieldType.image},
                    "dataset_id": str(dataset.id),
                    "inserted_at": image_field_a.inserted_at.isoformat(),
                    "updated_at": image_field_a.updated_at.isoformat(),
                },
                {
                    "id": str(image_field_b.id),
                    "name": image_field_b.name,
                    "title": image_field_b.title,
                    "required": False,
                    "settings": {"type": FieldType.image},
                    "dataset_id": str(dataset.id),
                    "inserted_at": image_field_b.inserted_at.isoformat(),
                    "updated_at": image_field_b.updated_at.isoformat(),
                },
            ]
        }
