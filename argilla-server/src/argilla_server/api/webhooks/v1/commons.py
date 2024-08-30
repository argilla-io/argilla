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
import httpx

from math import floor
from typing_extensions import Dict
from datetime import datetime, timezone

from standardwebhooks.webhooks import Webhook


# TODO: Get the webhook URL from the database.
# TODO: Add setting to enable/disable webhooks.
# TODO: Check if webhooks are enabled/disabled.
def notify_event(type: str, timestamp: datetime, data: Dict) -> httpx.Response:
    # TODO: Generate random message id
    msg_id = "msg_AFAlNySwBSr"

    payload = json.dumps(_build_payload(type, timestamp, data))

    # TODO: Obtain the webhook secret from the settings
    signature = Webhook("whsec_h7QRo0AFAlNySwBSr/XXXWFhh4cDlTo42PRPzXOT6SY=").sign(msg_id, timestamp, payload)

    # TODO: Obtain the webhook URL from the settings
    return httpx.post(
        "http://localhost:9000",
        headers=_build_headers(msg_id, timestamp, signature),
        content=payload,
    )


def _build_headers(msg_id: str, timestamp: datetime, signature: str) -> Dict:
    return {
        "content-type": "application/json",
        "webhook-id": msg_id,
        "webhook-timestamp": str(floor(timestamp.replace(tzinfo=timezone.utc).timestamp())),
        "webhook-signature": signature,
    }


def _build_payload(type: str, timestamp: datetime, data: Dict) -> Dict:
    return {
        "type": type,
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "data": data,
    }
