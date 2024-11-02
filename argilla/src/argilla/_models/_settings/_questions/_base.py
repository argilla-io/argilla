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
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_serializer, field_validator, Field
from pydantic_core.core_schema import ValidationInfo


class QuestionSettings(BaseModel, validate_assignment=True):
    type: str


class QuestionBaseModel(BaseModel, validate_assignment=True):
    id: Optional[UUID] = None
    name: str
    settings: QuestionSettings

    title: str = Field(None, validate_default=True)
    description: Optional[str] = None
    required: bool = True
    inserted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("title", mode="before")
    @classmethod
    def __title_default(cls, title, info: ValidationInfo):
        validated_title = title or info.data["name"]
        return validated_title

    @field_serializer("inserted_at", "updated_at", when_used="unless-none")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    @field_serializer("id", when_used="unless-none")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
