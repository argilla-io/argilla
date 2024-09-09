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

from datetime import datetime

from fastapi.encoders import jsonable_encoder

from argilla_server.models import Response, Webhook
from argilla_server.api.schemas.v1.responses import Response as ResponseSchema
from argilla_server.api.webhooks.v1.commons import notify_event
from argilla_server.api.webhooks.v1.enums import WebhookEvent


def notify_response_created_event(webhook: Webhook, response: Response) -> httpx.Response:
    return notify_event(
        webhook=webhook,
        type=WebhookEvent.response_created,
        timestamp=datetime.utcnow(),
        data=jsonable_encoder(ResponseSchema.from_orm(response)),
    )
