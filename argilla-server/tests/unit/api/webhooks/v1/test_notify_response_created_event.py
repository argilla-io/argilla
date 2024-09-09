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

from httpx import Response
from standardwebhooks.webhooks import Webhook

from argilla_server.enums import ResponseStatus
from argilla_server.api.webhooks.v1.enums import WebhookEvent
from argilla_server.api.webhooks.v1.responses import notify_response_created_event

from tests.factories import ResponseFactory, WebhookFactory


@pytest.mark.asyncio
class TestNotifyResponseCreatedEvent:
    async def test_notify_response_created_event(self, respx_mock):
        webhook = await WebhookFactory.create()
        response = await ResponseFactory.create()

        respx_mock.post(webhook.url).mock(return_value=Response(200))
        resp = notify_response_created_event(webhook, response)

        assert resp.status_code == 200

        request, _ = respx.calls.last
        timestamp = json.loads(request.content)["timestamp"]

        wh = Webhook(webhook.secret)
        assert wh.verify(headers=request.headers, data=request.content) == {
            "type": WebhookEvent.response_created,
            "timestamp": timestamp,
            "data": {
                "id": str(response.id),
                "values": None,
                "status": ResponseStatus.submitted,
                "record_id": str(response.record_id),
                "user_id": str(response.user_id),
                "inserted_at": response.inserted_at.isoformat(),
                "updated_at": response.updated_at.isoformat(),
            },
        }
