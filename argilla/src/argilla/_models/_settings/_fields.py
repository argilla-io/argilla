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

from typing import Optional, Literal, Annotated, Union
from uuid import UUID

from pydantic import BaseModel, field_serializer, field_validator, Field
from pydantic_core.core_schema import ValidationInfo

from argilla._helpers import log_message
from argilla._models import ResourceModel


class TextFieldSettings(BaseModel):
    type: Literal["text"] = "text"
    use_markdown: Optional[bool] = False


class ImageFieldSettings(BaseModel):
    type: Literal["image"] = "image"


class ChatFieldSettings(BaseModel):
    type: Literal["chat"] = "chat"
    use_markdown: Optional[bool] = True


FieldSettings = Annotated[
    Union[
        TextFieldSettings,
        ImageFieldSettings,
        ChatFieldSettings,
    ],
    Field(..., discriminator="type"),
]


class FieldModel(ResourceModel):
    name: str
    settings: FieldSettings
    title: Optional[str] = None
    required: bool = True
    description: Optional[str] = None
    dataset_id: Optional[UUID] = None

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
        log_message(f"TextField title is {validated_title}")
        return validated_title

    @field_serializer("id", "dataset_id", when_used="unless-none")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
