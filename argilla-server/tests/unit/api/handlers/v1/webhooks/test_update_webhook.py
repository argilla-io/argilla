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

from uuid import UUID, uuid4
from httpx import AsyncClient
from typing import Any

from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.constants import API_KEY_HEADER_NAME

from tests.factories import AdminFactory, AnnotatorFactory, WebhookFactory


@pytest.mark.asyncio
class TestUpdateWebhook:
    def url(self, webhook_id: UUID) -> str:
        return f"/api/v1/webhooks/{webhook_id}"

    async def test_update_webhook(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [
                    WebhookEvent.response_created,
                    WebhookEvent.response_updated,
                ],
                "enabled": False,
                "description": "Test webhook",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": "https://example.com/webhook",
            "secret": webhook.secret,
            "events": [
                WebhookEvent.response_created,
                WebhookEvent.response_updated,
            ],
            "enabled": False,
            "description": "Test webhook",
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

        assert webhook.url == "https://example.com/webhook"
        assert webhook.events == [
            WebhookEvent.response_created,
            WebhookEvent.response_updated,
        ]

    async def test_update_webhook_with_url(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": "https://example.com/webhook",
            "secret": webhook.secret,
            "events": webhook.events,
            "enabled": True,
            "description": None,
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

        assert webhook.url == "https://example.com/webhook"

    async def test_update_webhook_with_ip_address_url(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": "https://1.1.1.1:9999/webhook",
            },
        )

        assert response.status_code == 200
        assert response.json()["url"] == "https://1.1.1.1:9999/webhook"

    async def test_update_webhook_with_events(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "events": [WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": webhook.url,
            "secret": webhook.secret,
            "events": [WebhookEvent.response_updated],
            "enabled": True,
            "description": None,
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

        assert webhook.events == [WebhookEvent.response_updated]

    async def test_update_webhook_with_enabled(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "enabled": False,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": webhook.url,
            "secret": webhook.secret,
            "events": webhook.events,
            "enabled": False,
            "description": None,
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

        assert webhook.enabled == False

    async def test_update_webhook_with_description(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "description": "Test webhook",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": webhook.url,
            "secret": webhook.secret,
            "events": webhook.events,
            "enabled": True,
            "description": "Test webhook",
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

        assert webhook.description == "Test webhook"

    async def test_update_webhook_without_changes(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": webhook.url,
            "secret": webhook.secret,
            "events": webhook.events,
            "enabled": True,
            "description": None,
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

    async def test_update_webhook_as_admin(self, async_client: AsyncClient):
        admin = await AdminFactory.create()

        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 403

        assert webhook.url != "https://example.com/webhook"
        assert webhook.events != [WebhookEvent.response_updated]

    async def test_update_webhook_as_annotator(self, async_client: AsyncClient):
        annotator = await AnnotatorFactory.create()

        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 403

        assert webhook.url != "https://example.com/webhook"
        assert webhook.events != [WebhookEvent.response_updated]

    async def test_update_webhook_without_authentication(self, async_client: AsyncClient):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 401

        assert webhook.url != "https://example.com/webhook"
        assert webhook.events != [WebhookEvent.response_updated]

    @pytest.mark.parametrize("invalid_url", ["", "example.com", "http.example.com", "https.example.com"])
    async def test_update_webhook_with_invalid_url(
        self, async_client: AsyncClient, owner_auth_header: dict, invalid_url: str
    ):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": invalid_url,
                "events": [WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 422

        assert webhook.url != invalid_url
        assert webhook.events != [WebhookEvent.response_updated]

    @pytest.mark.parametrize(
        "invalid_events", [[], ["invalid_event"], [WebhookEvent.response_updated, "invalid_event"]]
    )
    async def test_update_webhook_with_invalid_events(
        self, async_client: AsyncClient, owner_auth_header: dict, invalid_events: list
    ):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": invalid_events,
            },
        )

        assert response.status_code == 422

        assert webhook.url != "https://example.com/webhook"
        assert webhook.events != invalid_events

    async def test_update_webhook_with_duplicated_events(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "events": [WebhookEvent.response_updated, WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 422
        assert webhook.events != [WebhookEvent.response_updated, WebhookEvent.response_updated]

    @pytest.mark.parametrize("invalid_enabled", ["", "invalid", 123])
    async def test_update_webhook_with_invalid_enabled(
        self, async_client: AsyncClient, owner_auth_header: dict, invalid_enabled: Any
    ):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "enabled": invalid_enabled,
            },
        )

        assert response.status_code == 422
        assert webhook.enabled != invalid_enabled

    @pytest.mark.parametrize("invalid_description", ["", "d" * 1001])
    async def test_update_webhook_with_invalid_description(
        self, async_client: AsyncClient, owner_auth_header: dict, invalid_description: str
    ):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "description": invalid_description,
            },
        )

        assert response.status_code == 422
        assert webhook.description != invalid_description

    async def test_update_webhook_with_url_as_none(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": None,
                "events": [WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 422

        assert webhook.url != None
        assert webhook.events != [WebhookEvent.response_updated]

    async def test_update_webhook_with_enabled_as_none(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "enabled": None,
            },
        )

        assert response.status_code == 422
        assert webhook.enabled != None

    async def test_update_webhook_with_events_as_none(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create()

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": None,
            },
        )

        assert response.status_code == 422

        assert webhook.url != "https://example.com/webhook"
        assert webhook.events != None

    async def test_update_webhook_with_description_as_none(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook = await WebhookFactory.create(description="Test webhook")

        response = await async_client.patch(
            self.url(webhook.id),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_updated],
                "description": None,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(webhook.id),
            "url": "https://example.com/webhook",
            "secret": webhook.secret,
            "events": [WebhookEvent.response_updated],
            "enabled": True,
            "description": None,
            "inserted_at": webhook.inserted_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
        }

        assert webhook.url == "https://example.com/webhook"
        assert webhook.events == [WebhookEvent.response_updated]
        assert webhook.description == None

    async def test_update_webhook_with_nonexistent_webhook_id(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook_id = uuid4()

        response = await async_client.patch(
            self.url(webhook_id),
            headers=owner_auth_header,
            json={
                "url": "https://example.com/webhook",
                "events": [WebhookEvent.response_updated],
            },
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Webhook with id `{webhook_id}` not found"}
