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
from uuid import UUID, uuid4
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.models import Webhook
from argilla_server.constants import API_KEY_HEADER_NAME

from tests.factories import AdminFactory, AnnotatorFactory, WebhookFactory


@pytest.mark.asyncio
class TestDeleteWebhook:
    def url(self, webhook_id: UUID) -> str:
        return f"/api/v1/webhooks/{webhook_id}"

    async def test_delete_webhook(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.delete(self.url(webhook.id), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": webhook.url,
            "secret": webhook.secret,
            "events": [WebhookEvent.response_created],
            "enabled": True,
            "description": None,
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    async def test_delete_webhook_as_admin(self, db: AsyncSession, async_client: AsyncClient):
        admin = await AdminFactory.create()

        webhook = await WebhookFactory.create()

        response = await async_client.delete(
            self.url(webhook.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 1

    async def test_delete_webhook_as_annotator(self, db: AsyncSession, async_client: AsyncClient):
        annotator = await AnnotatorFactory.create()

        webhook = await WebhookFactory.create()

        response = await async_client.delete(
            self.url(webhook.id),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 1

    async def test_delete_webhook_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        webhook = await WebhookFactory.create()

        response = await async_client.delete(self.url(webhook.id))

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 1

    async def test_delete_webhook_with_nonexistent_webhook_id(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook_id = uuid4()

        response = await async_client.delete(self.url(webhook_id), headers=owner_auth_header)

        assert response.status_code == 404
        assert response.json() == {"detail": f"Webhook with id `{webhook_id}` not found"}
