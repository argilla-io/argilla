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

import json
import secrets
import httpx

from math import floor
from typing_extensions import Dict
from datetime import datetime, timezone
from standardwebhooks.webhooks import Webhook

from argilla_server.models import Webhook as WebhookModel

MSG_ID_BYTES_LENGTH = 16

NOTIFY_EVENT_DEFAULT_TIMEOUT = httpx.Timeout(timeout=20.0)


# NOTE: We are using standard webhooks implementation.
# For more information take a look to https://www.standardwebhooks.com
def notify_event(webhook: WebhookModel, event: str, timestamp: datetime, data: Dict) -> httpx.Response:
    timestamp_attempt = datetime.utcnow()

    msg_id = _generate_msg_id()
    payload = json.dumps(_build_payload(event, timestamp, data))
    signature = Webhook(webhook.secret).sign(msg_id, timestamp_attempt, payload)

    return httpx.post(
        webhook.url,
        headers=_build_headers(msg_id, timestamp_attempt, signature),
        content=payload,
        timeout=NOTIFY_EVENT_DEFAULT_TIMEOUT,
    )


def _generate_msg_id() -> str:
    return f"msg_{secrets.token_urlsafe(MSG_ID_BYTES_LENGTH)}"


def _build_headers(msg_id: str, timestamp: datetime, signature: str) -> Dict:
    return {
        "webhook-id": msg_id,
        "webhook-timestamp": str(floor(timestamp.replace(tzinfo=timezone.utc).timestamp())),
        "webhook-signature": signature,
        "content-type": "application/json",
    }


def _build_payload(type: str, timestamp: datetime, data: Dict) -> Dict:
    return {
        "type": type,
        "version": 1,
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "data": data,
    }
