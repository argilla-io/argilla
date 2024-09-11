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
import respx
import json

from uuid import UUID, uuid4
from httpx import AsyncClient, Response
from standardwebhooks.webhooks import Webhook

from argilla_server.contexts import info
from argilla_server.constants import API_KEY_HEADER_NAME

from tests.factories import AdminFactory, AnnotatorFactory, WebhookFactory


@pytest.mark.asyncio
class TestPingWebhook:
    def url(self, webhook_id: UUID) -> str:
        return f"/api/v1/webhooks/{webhook_id}/ping"

    async def test_ping_webhook(self, async_client: AsyncClient, owner_auth_header: dict, respx_mock):
        webhook = await WebhookFactory.create()

        respx_mock.post(webhook.url).mock(return_value=Response(200))
        response = await async_client.post(
            self.url(webhook.id),
            headers=owner_auth_header,
        )

        assert response.status_code == 204

        request, _ = respx.calls.last
        timestamp = json.loads(request.content)["timestamp"]

        wh = Webhook(webhook.secret)
        assert wh.verify(headers=request.headers, data=request.content) == {
            "type": "ping",
            "version": 1,
            "timestamp": timestamp,
            "data": {
                "agent": "argilla-server",
                "version": info.argilla_version(),
            },
        }

    async def test_ping_webhook_as_admin(self, async_client: AsyncClient, respx_mock):
        admin = await AdminFactory.create()
        webhook = await WebhookFactory.create()

        respx_mock.post(webhook.url).mock(return_value=Response(200))
        response = await async_client.post(
            self.url(webhook.id),
            headers={API_KEY_HEADER_NAME: admin.api_key},
        )

        assert response.status_code == 403

    async def test_ping_webhook_as_annotator(self, async_client: AsyncClient):
        annotator = await AnnotatorFactory.create()
        webhook = await WebhookFactory.create()

        response = await async_client.post(
            self.url(webhook.id),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
        )

        assert response.status_code == 403

    async def test_ping_webhook_without_authentication(self, async_client: AsyncClient):
        webhook = await WebhookFactory.create()

        response = await async_client.post(self.url(webhook.id))

        assert response.status_code == 401

    async def test_ping_webhook_with_nonexistent_webhook_id(self, async_client: AsyncClient, owner_auth_header: dict):
        webhook_id = uuid4()

        response = await async_client.post(
            self.url(webhook_id),
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Webhook with id `{webhook_id}` not found"}
