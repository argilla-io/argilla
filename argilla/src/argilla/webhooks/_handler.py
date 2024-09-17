# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable, TYPE_CHECKING

from argilla.webhooks._event import WebhookEvent
from argilla.webhooks._resource import Webhook

if TYPE_CHECKING:
    from fastapi import Request


class WebhookHandler:
    def __init__(self, webhook: Webhook):
        self.webhook = webhook

    def handle(self, func: Callable, raw_event: bool = False) -> Callable:
        from fastapi import Request

        async def request_handler(request: Request):
            event = await self._verify_request(request)
            if event.type not in self.webhook.events:
                return

            if raw_event:
                return await func(event)

            return await func(**event.normalize(self.webhook._client))

        return request_handler

    async def _verify_request(self, request: "Request") -> WebhookEvent:
        """
        Verify the request signature and return the event object.

        Arguments:
            request (Request): The request object.

        Returns:
            WebhookEvent: The event object.
        """

        from standardwebhooks.webhooks import Webhook

        body = await request.body()
        headers = dict(request.headers)

        json = Webhook(whsecret=self.webhook.secret).verify(body, headers)
        return WebhookEvent.model_validate(json)
