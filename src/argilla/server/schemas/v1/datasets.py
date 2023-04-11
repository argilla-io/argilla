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
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import BaseModel, conlist, validator
from pydantic.utils import GetterDict

from argilla.server.models import AnnotationType

RATING_OPTIONS_MIN_ITEMS = 2
RATING_OPTIONS_MAX_ITEMS = 100


class Dataset(BaseModel):
    id: UUID
    name: str
    guidelines: Optional[str]
    workspace_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DatasetCreate(BaseModel):
    name: str
    guidelines: Optional[str]
    workspace_id: UUID


class RatingAnnotationSettingsOption(BaseModel):
    value: int


class RatingAnnotationSettings(BaseModel):
    options: conlist(
        item_type=RatingAnnotationSettingsOption,
        min_items=RATING_OPTIONS_MIN_ITEMS,
        max_items=RATING_OPTIONS_MAX_ITEMS,
    )


class TextAnnotationSettings(BaseModel):
    pass


class AnnotationGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "settings":
            if self._obj.type == AnnotationType.text:
                return TextAnnotationSettings()
            if self._obj.type == AnnotationType.rating:
                return RatingAnnotationSettings(**self._obj.settings)
        return super().get(key, default)


class Annotation(BaseModel):
    id: UUID
    name: str
    title: str
    type: AnnotationType
    required: bool
    settings: Union[RatingAnnotationSettings, TextAnnotationSettings]
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        getter_dict = AnnotationGetter


class AnnotationCreate(BaseModel):
    name: str
    title: str
    type: AnnotationType
    required: Optional[bool]
    settings: Optional[Union[RatingAnnotationSettings, TextAnnotationSettings]]

    @validator("settings", pre=True, always=True)
    def validate_settings(cls, settings: Any, values):
        if settings and not isinstance(settings, dict):
            return settings

        type = values.get("type")

        if type == AnnotationType.text:
            return {}
        if type == AnnotationType.rating:
            return RatingAnnotationSettings(**settings)
        else:
            return settings
