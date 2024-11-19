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

from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.constants import API_KEY_HEADER_NAME

from tests.factories import AdminFactory, AnnotatorFactory, WebhookFactory


@pytest.mark.asyncio
class TestListWebhooks:
    def url(self) -> str:
        return "/api/v1/webhooks"

    async def test_list_webhooks(self, async_client: AsyncClient, owner_auth_header: dict):
        webhooks = await WebhookFactory.create_batch(2)

        response = await async_client.get(self.url(), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(webhooks[0].id),
                    "url": webhooks[0].url,
                    "secret": webhooks[0].secret,
                    "events": [WebhookEvent.response_created],
                    "enabled": True,
                    "description": None,
                    "inserted_at": webhooks[0].inserted_at.isoformat(),
                    "updated_at": webhooks[0].updated_at.isoformat(),
                },
                {
                    "id": str(webhooks[1].id),
                    "url": webhooks[1].url,
                    "secret": webhooks[1].secret,
                    "events": [WebhookEvent.response_created],
                    "enabled": True,
                    "description": None,
                    "inserted_at": webhooks[1].inserted_at.isoformat(),
                    "updated_at": webhooks[1].updated_at.isoformat(),
                },
            ],
        }

    async def test_list_webhooks_without_webhooks(self, async_client: AsyncClient, owner_auth_header: dict):
        response = await async_client.get(self.url(), headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {"items": []}

    async def test_list_webhooks_as_admin(self, async_client: AsyncClient):
        admin = await AdminFactory.create()

        response = await async_client.get(
            self.url(),
            headers={API_KEY_HEADER_NAME: admin.api_key},
        )

        assert response.status_code == 403

    async def test_list_webhooks_as_annotator(self, async_client: AsyncClient):
        annotator = await AnnotatorFactory.create()

        response = await async_client.get(
            self.url(),
            headers={API_KEY_HEADER_NAME: annotator.api_key},
        )

        assert response.status_code == 403

    async def test_list_webhooks_without_authentication(self, async_client: AsyncClient):
        response = await async_client.get(self.url())

        assert response.status_code == 401
