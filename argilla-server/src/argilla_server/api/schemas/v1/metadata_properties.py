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
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar, Union
from uuid import UUID

from argilla_server.api.schemas.v1.commons import UpdateSchema
from argilla_server.enums import MetadataPropertyType
from pydantic import BaseModel, Field, constr, ConfigDict, field_validator, model_validator

FLOAT_METADATA_METRICS_PRECISION = 5

METADATA_PROPERTY_CREATE_NAME_MIN_LENGTH = 1
METADATA_PROPERTY_CREATE_NAME_MAX_LENGTH = 200

METADATA_PROPERTY_CREATE_TITLE_MIN_LENGTH = 1
METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH = 500

TERMS_METADATA_PROPERTY_VALUES_MIN_ITEMS = 1
TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS = 250

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


class TermsMetadataMetrics(BaseModel):
    class TermCount(BaseModel):
        term: Any
        count: int

    type: Literal[MetadataPropertyType.terms] = MetadataPropertyType.terms
    total: int
    values: List[TermCount] = Field(default_factory=list)


NT = TypeVar("NT", int, float)


class NumericMetadataMetrics(BaseModel, Generic[NT]):
    min: Optional[NT] = None
    max: Optional[NT] = None


class IntegerMetadataMetrics(NumericMetadataMetrics[int]):
    type: Literal[MetadataPropertyType.integer] = MetadataPropertyType.integer


class FloatMetadataMetrics(NumericMetadataMetrics[float]):
    type: Literal[MetadataPropertyType.float] = MetadataPropertyType.float

    @field_validator("min", "max")
    @classmethod
    def round_result(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            return round(v, FLOAT_METADATA_METRICS_PRECISION)
        return v


MetadataMetrics = Annotated[
    Union[
        TermsMetadataMetrics,
        IntegerMetadataMetrics,
        FloatMetadataMetrics,
    ],
    Field(..., discriminator="type"),
]


class TermsMetadataProperty(BaseModel):
    type: Literal[MetadataPropertyType.terms]
    values: Optional[List[Any]] = None


class IntegerMetadataProperty(BaseModel):
    type: Literal[MetadataPropertyType.integer]
    min: Optional[int] = None
    max: Optional[int] = None


class FloatMetadataProperty(BaseModel):
    type: Literal[MetadataPropertyType.float]
    min: Optional[float] = None
    max: Optional[float] = None


MetadataPropertySettings = Annotated[
    Union[TermsMetadataProperty, IntegerMetadataProperty, FloatMetadataProperty],
    Field(..., discriminator="type"),
]

MetadataPropertyName = Annotated[
    str,
    Field(
        ...,
        min_length=METADATA_PROPERTY_CREATE_NAME_MIN_LENGTH,
        max_length=METADATA_PROPERTY_CREATE_NAME_MAX_LENGTH,
    ),
]

MetadataPropertyTitle = Annotated[
    constr(min_length=METADATA_PROPERTY_CREATE_TITLE_MIN_LENGTH, max_length=METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH),
    Field(..., description="The title of the metadata property"),
]


class NumericMetadataProperty(BaseModel, Generic[NT]):
    min: Optional[NT] = None
    max: Optional[NT] = None

    @model_validator(mode="after")
    @classmethod
    def check_bounds(cls, instance: "NumericMetadataProperty") -> "NumericMetadataProperty":
        min = instance.min
        max = instance.max

        if min is not None and max is not None and min >= max:
            raise ValueError(f"'min' ({min}) must be lower than 'max' ({max})")

        return instance


class TermsMetadataPropertyCreate(BaseModel):
    type: Literal[MetadataPropertyType.terms]
    values: Optional[List[Any]] = Field(
        None,
        min_length=TERMS_METADATA_PROPERTY_VALUES_MIN_ITEMS,
        max_length=TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS,
    )


class IntegerMetadataPropertyCreate(NumericMetadataProperty[int]):
    type: Literal[MetadataPropertyType.integer]


class FloatMetadataPropertyCreate(NumericMetadataProperty[float]):
    type: Literal[MetadataPropertyType.float]


MetadataPropertySettingsCreate = Annotated[
    Union[TermsMetadataPropertyCreate, IntegerMetadataPropertyCreate, FloatMetadataPropertyCreate],
    Field(..., discriminator="type"),
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

    model_config = ConfigDict(from_attributes=True)


class MetadataProperties(BaseModel):
    items: List[MetadataProperty]


class MetadataPropertyCreate(BaseModel):
    name: MetadataPropertyName
    title: MetadataPropertyTitle
    settings: MetadataPropertySettingsCreate
    visible_for_annotators: bool = True


class MetadataPropertyUpdate(UpdateSchema):
    title: Optional[MetadataPropertyTitle] = None
    visible_for_annotators: Optional[bool] = None

    __non_nullable_fields__ = {"title", "visible_for_annotators"}
