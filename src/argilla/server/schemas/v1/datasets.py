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
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, conlist, validator

from argilla.server.models import AnnotationType, DatasetStatus

RATING_OPTIONS_MIN_ITEMS = 2
RATING_OPTIONS_MAX_ITEMS = 100


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


class DatasetCreate(BaseModel):
    name: str
    guidelines: Optional[str]
    workspace_id: UUID


class Annotation(BaseModel):
    id: UUID
    name: str
    title: str
    type: AnnotationType
    required: bool
    settings: dict
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RatingAnnotationSettingsOptionCreate(BaseModel):
    value: int


class RatingAnnotationSettingsCreate(BaseModel):
    options: conlist(
        item_type=RatingAnnotationSettingsOptionCreate,
        min_items=RATING_OPTIONS_MIN_ITEMS,
        max_items=RATING_OPTIONS_MAX_ITEMS,
    )


class AnnotationCreate(BaseModel):
    name: str
    title: str
    type: AnnotationType
    required: Optional[bool]
    settings: Optional[dict] = {}

    @validator("settings", always=True)
    def validate_settings(cls, settings: dict, values):
        type = values.get("type")

        if type == AnnotationType.text:
            return {}
        if type == AnnotationType.rating:
            return RatingAnnotationSettingsCreate(**settings).dict()
        else:
            return settings
