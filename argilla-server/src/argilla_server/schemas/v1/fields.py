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
from typing import Annotated, List, Literal, Optional
from uuid import UUID

from typing_extensions import Annotated

from argilla_server.enums import FieldType
from argilla_server.pydantic_v1 import BaseModel, constr
from argilla_server.pydantic_v1 import Field as PydanticField
from argilla_server.schemas.base import UpdateSchema

FIELD_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"
FIELD_CREATE_NAME_MIN_LENGTH = 1
FIELD_CREATE_NAME_MAX_LENGTH = 200

FIELD_CREATE_TITLE_MIN_LENGTH = 1
FIELD_CREATE_TITLE_MAX_LENGTH = 500


FieldName = Annotated[
    constr(
        regex=FIELD_CREATE_NAME_REGEX,
        min_length=FIELD_CREATE_NAME_MIN_LENGTH,
        max_length=FIELD_CREATE_NAME_MAX_LENGTH,
    ),
    PydanticField(..., description="The name of the field"),
]


FieldTitle = Annotated[
    constr(
        min_length=FIELD_CREATE_TITLE_MIN_LENGTH,
        max_length=FIELD_CREATE_TITLE_MAX_LENGTH,
    ),
    PydanticField(..., description="The title of the field"),
]


class TextFieldSettings(BaseModel):
    type: Literal[FieldType.text]
    use_markdown: bool = False


class TextFieldSettingsUpdate(UpdateSchema):
    type: Literal[FieldType.text]
    use_markdown: bool


class Field(BaseModel):
    id: UUID
    name: str
    title: str
    required: bool
    settings: TextFieldSettings
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Fields(BaseModel):
    items: List[Field]


class FieldCreate(BaseModel):
    name: FieldName
    title: FieldTitle
    required: Optional[bool]
    settings: TextFieldSettings


class FieldUpdate(UpdateSchema):
    title: Optional[FieldTitle]
    settings: Optional[TextFieldSettingsUpdate]

    __non_nullable_fields__ = {"title", "settings"}
