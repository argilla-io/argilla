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
from typing import Generic, List, Literal, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from argilla.server.enums import MetadataPropertyType
from argilla.server.schemas.base import UpdateSchema
from argilla.server.schemas.v1.datasets import MetadataPropertySettings, MetadataPropertyTitle

FLOAT_METADATA_METRICS_PRECISION = 5

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


class TermsMetadataMetrics(BaseModel):
    class TermCount(BaseModel):
        term: str
        count: int

    type: Literal[MetadataPropertyType.terms] = Field(MetadataPropertyType.terms, const=True)
    total: int
    values: List[TermCount] = Field(default_factory=list)


NT = TypeVar("NT", int, float)


class NumericMetadataMetrics(GenericModel, Generic[NT]):
    min: Optional[NT]
    max: Optional[NT]


class IntegerMetadataMetrics(NumericMetadataMetrics[int]):
    type: Literal[MetadataPropertyType.integer] = Field(MetadataPropertyType.integer, const=True)


class FloatMetadataMetrics(NumericMetadataMetrics[float]):
    type: Literal[MetadataPropertyType.float] = Field(MetadataPropertyType.float, const=True)

    @validator("min", "max")
    def round_result(cls, v: float):
        if v is not None:
            return round(v, FLOAT_METADATA_METRICS_PRECISION)
        return v


MetadataMetrics = Annotated[
    Union[TermsMetadataMetrics, IntegerMetadataMetrics, FloatMetadataMetrics], Field(..., discriminator="type")
]


class MetadataProperty(BaseModel):
    id: UUID
    name: str
    title: str
    settings: MetadataPropertySettings
    visible_for_annotators: bool
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class MetadataPropertyUpdate(UpdateSchema):
    title: Optional[MetadataPropertyTitle]
    visible_for_annotators: Optional[bool]

    __non_nullable_fields__ = {"title", "visible_for_annotators"}
