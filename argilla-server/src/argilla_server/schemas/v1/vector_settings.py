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
from typing import Annotated, List, Optional
from uuid import UUID

from typing_extensions import Annotated

from argilla_server.pydantic_v1 import BaseModel, Field, PositiveInt, constr
from argilla_server.schemas.base import UpdateSchema

VECTOR_SETTINGS_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"
VECTOR_SETTINGS_CREATE_NAME_MIN_LENGTH = 1
VECTOR_SETTINGS_CREATE_NAME_MAX_LENGTH = 200

VECTOR_SETTINGS_CREATE_TITLE_MIN_LENGTH = 1
VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH = 500


VectorSettingsTitle = Annotated[
    constr(
        min_length=VECTOR_SETTINGS_CREATE_TITLE_MIN_LENGTH,
        max_length=VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH,
    ),
    Field(..., description="The title of the vector settings"),
]


class VectorSettings(BaseModel):
    id: UUID
    name: str
    title: str
    dimensions: int
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

    def check_vector(self, value: List[float]) -> None:
        num_elements = len(value)

        if num_elements != self.dimensions:
            raise ValueError(f"vector must have {self.dimensions} elements, got {num_elements} elements")


class VectorsSettings(BaseModel):
    items: List[VectorSettings]


class VectorSettingsCreate(BaseModel):
    name: str = Field(
        ...,
        regex=VECTOR_SETTINGS_CREATE_NAME_REGEX,
        min_length=VECTOR_SETTINGS_CREATE_NAME_MIN_LENGTH,
        max_length=VECTOR_SETTINGS_CREATE_NAME_MAX_LENGTH,
        description="The title of the vector settings",
    )
    title: VectorSettingsTitle
    dimensions: PositiveInt


class VectorSettingsUpdate(UpdateSchema):
    title: Optional[VectorSettingsTitle]

    __non_nullable_fields__ = {"title"}
