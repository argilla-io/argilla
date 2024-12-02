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

from typing import Any
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.models import Webhook
from argilla_server.constants import API_KEY_HEADER_NAME

from tests.factories import AdminFactory, AnnotatorFactory, WebhookFactory


@pytest.mark.asyncio
class TestCreateWebhook:
    def url(self) -> str:
        return "/api/v1/webhooks"

    async def test_create_webhook(self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created],
                "description": "Test webhook",
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 1
        webhook = (await db.execute(select(Webhook))).scalar_one()

        assert response.json() == {
            "id": str(webhook.id),
            "url": "https://example.com/webhook",
            "secret": webhook.secret,
            "events": [WebhookEvent.response_created],
            "enabled": True,
            "description": "Test webhook",
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

    async def test_create_webhook_with_ip_address_url(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "http://1.1.1.1/webhook",
                "events": [WebhookEvent.response_created],
                "description": "Test webhook",
            },
        )

        assert response.status_code == 201

        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 1
        webhook = (await db.execute(select(Webhook))).scalar_one()

        assert response.json()["url"] == "http://1.1.1.1/webhook"

    async def test_create_webhook_as_admin(self, db: AsyncSession, async_client: AsyncClient):
        admin = await AdminFactory.create()

        response = await async_client.post(
            self.url(),
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created],
            },
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    async def test_create_webhook_as_annotator(self, db: AsyncSession, async_client: AsyncClient):
        annotator = await AnnotatorFactory.create()

        response = await async_client.post(
            self.url(),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created],
            },
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    async def test_create_webhook_without_authentication(self, db: AsyncSession, async_client: AsyncClient):
        response = await async_client.post(
            self.url(),
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created],
            },
        )

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "invalid_url",
        [
            "",
            "example.com",
            "http.example.com",
            "https.example.com",
        ],
    )
    async def test_create_webhook_with_invalid_url(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict, invalid_url: str
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": invalid_url,
                "events": [WebhookEvent.response_created],
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    @pytest.mark.parametrize(
        "invalid_events", [[], ["invalid-event"], [WebhookEvent.response_created, "invalid-event"]]
    )
    async def test_create_webhook_with_invalid_events(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict, invalid_events: list
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": invalid_events,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    async def test_create_webhook_with_duplicated_events(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created, WebhookEvent.response_created],
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    @pytest.mark.parametrize("invalid_description", ["", "d" * 1001])
    async def test_create_webhook_with_invalid_description(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict, invalid_description: str
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created],
                "description": invalid_description,
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    async def test_create_webhook_with_description_as_none(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created],
                "description": None,
            },
        )

        assert response.status_code == 201
        assert response.json()["description"] == None

        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 1
        webhook = (await db.execute(select(Webhook))).scalar_one()
        assert webhook.description == None

    async def test_create_webhook_without_url(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "events": [WebhookEvent.response_created],
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    async def test_create_webhook_without_events(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
            },
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 0

    async def test_create_webhook_reaching_maximum_number_of_webhooks(
        self, db: AsyncSession, async_client: AsyncClient, owner_auth_header: dict
    ):
        await WebhookFactory.create_batch(10)

        response = await async_client.post(
            self.url(),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_created],
                "description": "Test webhook",
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "You can't create more than 10 webhooks. Please delete some of them first"}

        assert (await db.execute(select(func.count(Webhook.id)))).scalar() == 10
