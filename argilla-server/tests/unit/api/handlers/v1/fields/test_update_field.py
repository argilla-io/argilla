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
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Any
from uuid import UUID

from argilla_server.enums import FieldType

from tests.factories import ImageFieldFactory, ChatFieldFactory


@pytest.mark.asyncio
class TestUpdateField:
    def url(self, field_id: UUID) -> str:
        return f"/api/v1/fields/{field_id}"

    async def test_update_image_field(self, async_client: AsyncClient, owner_auth_header: dict):
        image_field = await ImageFieldFactory.create()

        response = await async_client.patch(
            self.url(image_field.id),
            headers=owner_auth_header,
            json={
                "title": "Updated title",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(image_field.id),
            "name": image_field.name,
            "title": "Updated title",
            "required": False,
            "settings": {"type": FieldType.image},
            "dataset_id": str(image_field.dataset_id),
            "inserted_at": image_field.inserted_at.isoformat(),
            "updated_at": image_field.updated_at.isoformat(),
        }

    async def test_update_chat_field_title(self, async_client: AsyncClient, owner_auth_header: dict):
        chat_field = await ChatFieldFactory.create()

        response = await async_client.patch(
            self.url(chat_field.id),
            headers=owner_auth_header,
            json={
                "title": "Updated title",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(chat_field.id),
            "name": chat_field.name,
            "title": "Updated title",
            "required": False,
            "settings": chat_field.settings,
            "dataset_id": str(chat_field.dataset_id),
            "inserted_at": chat_field.inserted_at.isoformat(),
            "updated_at": chat_field.updated_at.isoformat(),
        }

    async def test_update_chat_field_use_markdown(self, async_client: AsyncClient, owner_auth_header: dict):
        chat_field = await ChatFieldFactory.create(
            settings={
                "type": FieldType.chat,
                "use_markdown": True,
            }
        )

        response = await async_client.patch(
            self.url(chat_field.id),
            headers=owner_auth_header,
            json={
                "settings": {
                    "type": "chat",
                    "use_markdown": False,
                }
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(chat_field.id),
            "name": chat_field.name,
            "title": chat_field.title,
            "required": False,
            "settings": {"type": FieldType.chat, "use_markdown": False},
            "dataset_id": str(chat_field.dataset_id),
            "inserted_at": chat_field.inserted_at.isoformat(),
            "updated_at": chat_field.updated_at.isoformat(),
        }
