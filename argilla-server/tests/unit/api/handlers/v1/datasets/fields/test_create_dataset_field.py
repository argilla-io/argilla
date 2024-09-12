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

from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Any
from uuid import UUID
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import func, select

from argilla_server.enums import FieldType
from argilla_server.models import Field

from tests.factories import DatasetFactory


@pytest.mark.asyncio
class TestCreateDatasetField:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/fields"

    async def test_create_dataset_image_field(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "required": True,
                "settings": {"type": FieldType.image},
            },
        )

        image_field = (await db.execute(select(Field))).scalar_one()

        assert response.status_code == 201
        assert response.json() == {
            "id": str(image_field.id),
            "name": "name",
            "title": "title",
            "required": True,
            "settings": {"type": FieldType.image},
            "dataset_id": str(dataset.id),
            "inserted_at": image_field.inserted_at.isoformat(),
            "updated_at": image_field.updated_at.isoformat(),
        }

    async def test_create_dataset_chat_field(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "required": True,
                "settings": {"type": FieldType.chat},
            },
        )

        chat_field = (await db.execute(select(Field))).scalar_one()

        assert response.status_code == 201
        assert response.json() == {
            "id": str(chat_field.id),
            "name": "name",
            "title": "title",
            "required": True,
            "settings": {"type": FieldType.chat, "use_markdown": True},
            "dataset_id": str(dataset.id),
            "inserted_at": chat_field.inserted_at.isoformat(),
            "updated_at": chat_field.updated_at.isoformat(),
        }

    async def test_create_dataset_chat_field_with_use_markdown(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.post(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "name": "name",
                "title": "title",
                "required": True,
                "settings": {"type": FieldType.chat, "use_markdown": False},
            },
        )

        chat_field = (await db.execute(select(Field))).scalar_one()

        assert response.status_code == 201
        assert response.json() == {
            "id": str(chat_field.id),
            "name": "name",
            "title": "title",
            "required": True,
            "settings": {"type": FieldType.chat, "use_markdown": False},
            "dataset_id": str(dataset.id),
            "inserted_at": chat_field.inserted_at.isoformat(),
            "updated_at": chat_field.updated_at.isoformat(),
        }
