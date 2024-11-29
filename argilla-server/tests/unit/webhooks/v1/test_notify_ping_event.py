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

from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.webhooks.v1.ping import notify_ping_event
from argilla_server.contexts import info

from tests.factories import WebhookFactory


@pytest.mark.asyncio
class TestNotifyPingEvent:
    async def test_notify_ping_event(self, respx_mock):
        webhook = await WebhookFactory.create()

        respx_mock.post(webhook.url).mock(return_value=Response(200))
        response = notify_ping_event(webhook)

        assert response.status_code == 200

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
