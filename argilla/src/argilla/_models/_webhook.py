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

from enum import Enum
from typing import List, Optional

from pydantic import Field, ConfigDict

from argilla._models._base import ResourceModel


class EventType(str, Enum):
    dataset_created = "dataset.created"
    dataset_updated = "dataset.updated"
    dataset_deleted = "dataset.deleted"
    dataset_published = "dataset.published"

    record_created = "record.created"
    record_updated = "record.updated"
    record_deleted = "record.deleted"
    record_completed = "record.completed"

    response_created = "response.created"
    response_updated = "response.updated"
    response_deleted = "response.deleted"

    @property
    def resource(self) -> str:
        """
        Get the instance type of the event.

        Returns:
            str: The instance type. It can be "dataset", "record", or "response".

        """
        return self.split(".")[0]

    @property
    def action(self) -> str:
        """
        Get the action type of the event.

        Returns:
            str: The action type. It can be "created", "updated", "deleted", "published",  or "completed".

        """
        return self.split(".")[1]


class WebhookModel(ResourceModel):
    url: str
    events: List[EventType]
    enabled: bool = True
    description: Optional[str] = None

    secret: Optional[str] = Field(None, description="Webhook secret. Read-only.")

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )
