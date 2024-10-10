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

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.api.schemas.v1.commons import UpdateSchema
from argilla_server.pydantic_v1 import BaseModel, Field, HttpUrl

WEBHOOK_EVENTS_MIN_ITEMS = 1
WEBHOOK_DESCRIPTION_MIN_LENGTH = 1
WEBHOOK_DESCRIPTION_MAX_LENGTH = 1000


class Webhook(BaseModel):
    id: UUID
    url: str
    secret: str
    events: List[WebhookEvent]
    enabled: bool
    description: Optional[str]
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Webhooks(BaseModel):
    items: List[Webhook]


class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[WebhookEvent] = Field(
        min_items=WEBHOOK_EVENTS_MIN_ITEMS,
        unique_items=True,
    )
    description: Optional[str] = Field(
        min_length=WEBHOOK_DESCRIPTION_MIN_LENGTH,
        max_length=WEBHOOK_DESCRIPTION_MAX_LENGTH,
    )


class WebhookUpdate(UpdateSchema):
    url: Optional[HttpUrl]
    events: Optional[List[WebhookEvent]] = Field(
        min_items=WEBHOOK_EVENTS_MIN_ITEMS,
        unique_items=True,
    )
    enabled: Optional[bool]
    description: Optional[str] = Field(
        min_length=WEBHOOK_DESCRIPTION_MIN_LENGTH,
        max_length=WEBHOOK_DESCRIPTION_MAX_LENGTH,
    )

    __non_nullable_fields__ = {"url", "events", "enabled"}
