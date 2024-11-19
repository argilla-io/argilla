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

from uuid import UUID
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator, field_serializer

from argilla_server.webhooks.v1.enums import WebhookEvent
from argilla_server.api.schemas.v1.commons import UpdateSchema


WEBHOOK_EVENTS_MIN_ITEMS = 1
WEBHOOK_DESCRIPTION_MIN_LENGTH = 1
WEBHOOK_DESCRIPTION_MAX_LENGTH = 1000


class Webhook(BaseModel):
    id: UUID
    url: str
    secret: str
    events: List[WebhookEvent]
    enabled: bool
    description: Optional[str] = None
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Webhooks(BaseModel):
    items: List[Webhook]


class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[WebhookEvent] = Field(min_length=WEBHOOK_EVENTS_MIN_ITEMS)
    description: Optional[str] = Field(
        None,
        min_length=WEBHOOK_DESCRIPTION_MIN_LENGTH,
        max_length=WEBHOOK_DESCRIPTION_MAX_LENGTH,
    )

    @field_validator("events")
    @classmethod
    def events_must_be_unique(cls, events: List[WebhookEvent]):
        if len(set(events)) != len(events):
            raise ValueError("Events must be unique")

        return events

    @field_serializer("url")
    def serialize_url(self, url: HttpUrl):
        return str(url)


class WebhookUpdate(UpdateSchema):
    url: Optional[HttpUrl] = None
    events: Optional[List[WebhookEvent]] = Field(None, min_length=WEBHOOK_EVENTS_MIN_ITEMS)
    enabled: Optional[bool] = None
    description: Optional[str] = Field(
        None,
        min_length=WEBHOOK_DESCRIPTION_MIN_LENGTH,
        max_length=WEBHOOK_DESCRIPTION_MAX_LENGTH,
    )

    __non_nullable_fields__ = {"url", "events", "enabled"}

    @field_validator("events")
    @classmethod
    def events_must_be_unique(cls, events: Optional[List[WebhookEvent]]):
        if events is None:
            return None

        if len(set(events)) != len(events):
            raise ValueError("Events must be unique")

        return events

    @field_serializer("url")
    def serialize_url(self, url: Optional[HttpUrl]):
        if url is None:
            return None

        return str(url)
