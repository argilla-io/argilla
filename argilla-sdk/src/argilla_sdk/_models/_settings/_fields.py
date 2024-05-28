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

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_serializer, field_validator, Field
from pydantic_core.core_schema import ValidationInfo

from argilla_sdk._helpers._log import log


class FieldSettings(BaseModel):
    type: str = Field(validate_default=True)
    use_markdown: Optional[bool] = False


class FieldBaseModel(BaseModel):
    id: Optional[UUID] = None
    name: str

    title: Optional[str] = None
    required: bool = True
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def __name_lower(cls, name):
        formatted_name = name.lower().replace(" ", "_")
        return formatted_name

    @field_validator("title")
    @classmethod
    def __title_default(cls, title: str, info: ValidationInfo) -> str:
        data = info.data
        validated_title = title or data["name"]
        log(f"TextField title is {validated_title}")
        return validated_title

    @field_serializer("id", when_used="unless-none")
    def serialize_id(self, value: UUID) -> str:
        return str(value)


class TextFieldModel(FieldBaseModel):
    settings: FieldSettings = FieldSettings(type="text", use_markdown=False)


FieldModel = TextFieldModel
