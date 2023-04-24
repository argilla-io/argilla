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
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, conlist, constr
from pydantic import Field as ModelField
from typing_extensions import Literal

from argilla.server.models import AnnotationType, DatasetStatus, FieldType

ANNOTATION_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"

ANNOTATION_CREATE_NAME_MIN_LENGTH = 1
ANNOTATION_CREATE_NAME_MAX_LENGTH = 200

RATING_OPTIONS_MIN_ITEMS = 2
RATING_OPTIONS_MAX_ITEMS = 100

RECORDS_CREATE_MIN_ITEMS = 1
RECORDS_CREATE_MAX_ITEMS = 1000


class Dataset(BaseModel):
    id: UUID
    name: str
    guidelines: Optional[str]
    status: DatasetStatus
    workspace_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Datasets(BaseModel):
    items: List[Dataset]


class DatasetCreate(BaseModel):
    name: str
    guidelines: Optional[str]
    workspace_id: UUID


class TextFieldSettings(BaseModel):
    type: Literal[FieldType.text]


class Field(BaseModel):
    id: UUID
    name: str
    title: str
    required: bool
    settings: TextFieldSettings
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Fields(BaseModel):
    items: List[Field]


class TextAnnotationSettings(BaseModel):
    type: Literal[AnnotationType.text]


class RatingAnnotationSettingsOption(BaseModel):
    value: int


class RatingAnnotationSettings(BaseModel):
    type: Literal[AnnotationType.rating]
    options: conlist(
        item_type=RatingAnnotationSettingsOption,
        min_items=RATING_OPTIONS_MIN_ITEMS,
        max_items=RATING_OPTIONS_MAX_ITEMS,
    )


class Annotation(BaseModel):
    id: UUID
    name: str
    title: str
    required: bool
    settings: Union[TextAnnotationSettings, RatingAnnotationSettings] = ModelField(..., discriminator="type")
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Annotations(BaseModel):
    items: List[Annotation]


class AnnotationCreate(BaseModel):
    name: constr(
        regex=ANNOTATION_CREATE_NAME_REGEX,
        min_length=ANNOTATION_CREATE_NAME_MIN_LENGTH,
        max_length=ANNOTATION_CREATE_NAME_MAX_LENGTH,
    )
    title: str
    required: Optional[bool]
    settings: Union[TextAnnotationSettings, RatingAnnotationSettings] = ModelField(..., discriminator="type")


class Response(BaseModel):
    id: UUID
    values: Dict[str, Any]
    user_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RecordInclude(str, Enum):
    responses = "responses"


class Record(BaseModel):
    id: UUID
    fields: Dict[str, Any]
    external_id: Optional[str]
    responses: Optional[List[Response]]
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Records(BaseModel):
    items: List[Record]
    total: int


class ResponseCreate(BaseModel):
    values: Dict[str, Any]


class RecordCreate(BaseModel):
    fields: Dict[str, Any]
    external_id: Optional[str]
    response: Optional[ResponseCreate]


class RecordsCreate(BaseModel):
    items: conlist(item_type=RecordCreate, min_items=RECORDS_CREATE_MIN_ITEMS, max_items=RECORDS_CREATE_MAX_ITEMS)
