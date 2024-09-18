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

from datetime import datetime
from typing import Literal
from typing import Optional
from uuid import UUID

from pydantic import field_serializer, ConfigDict

from argilla._models import ResourceModel

__all__ = ["DatasetModel"]

from argilla._models._settings._task_distribution import TaskDistributionModel


class DatasetModel(ResourceModel):
    name: str
    status: Literal["draft", "ready"] = "draft"

    guidelines: Optional[str] = None
    allow_extra_metadata: bool = True  # Ideally, the default value should be provided by the server
    distribution: Optional[TaskDistributionModel] = None
    workspace_id: Optional[UUID] = None
    last_activity_at: Optional[datetime] = None

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @field_serializer("last_activity_at", when_used="unless-none")
    def serialize_last_activity_at(self, value: datetime) -> str:
        return value.isoformat()

    @field_serializer("workspace_id", when_used="unless-none")
    def serialize_workspace_id(self, value: UUID) -> str:
        return str(value)
