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

from enum import Enum
from typing import List, Literal, Optional, Union, Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator

from argilla._exceptions import MetadataError
from argilla._models import ResourceModel


class MetadataPropertyType(str, Enum):
    terms = "terms"
    integer = "integer"
    float = "float"


class BaseMetadataPropertySettings(BaseModel):
    type: MetadataPropertyType
    visible_for_annotators: Optional[bool] = True


class TermsMetadataPropertySettings(BaseMetadataPropertySettings):
    type: Literal[MetadataPropertyType.terms]
    values: Optional[List[Any]] = None

    @field_validator("values")
    @classmethod
    def __validate_values(cls, values):
        if values is None:
            return None
        if not isinstance(values, list):
            raise ValueError(f"values must be a list, got {type(values)}")
        return values


class NumericMetadataPropertySettings(BaseMetadataPropertySettings):
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None

    @model_validator(mode="before")
    @classmethod
    def __validate_min_max(cls, values):
        min_value = values.get("min")
        max_value = values.get("max")

        if min_value is not None and max_value is not None:
            if min_value >= max_value:
                raise MetadataError("min must be less than max.")
        return values


class IntegerMetadataPropertySettings(NumericMetadataPropertySettings):
    type: Literal[MetadataPropertyType.integer]

    @model_validator(mode="before")
    @classmethod
    def __validate_min_max(cls, values):
        min_value = values.get("min")
        max_value = values.get("max")

        if not all(isinstance(value, int) or value is None for value in [min_value, max_value]):
            raise MetadataError("min and max must be integers.")
        return values


class FloatMetadataPropertySettings(NumericMetadataPropertySettings):
    type: Literal[MetadataPropertyType.float]


MetadataPropertySettings = Annotated[
    Union[
        TermsMetadataPropertySettings,
        IntegerMetadataPropertySettings,
        FloatMetadataPropertySettings,
    ],
    Field(..., discriminator="type"),
]


class MetadataFieldModel(ResourceModel):
    """The schema definition of a metadata field in an Argilla dataset."""

    name: str
    settings: MetadataPropertySettings

    type: Optional[MetadataPropertyType] = Field(None, validate_default=True)
    title: Optional[str] = None
    visible_for_annotators: Optional[bool] = True

    dataset_id: Optional[UUID] = None

    @field_validator("name")
    @classmethod
    def __name_lower(cls, name):
        formatted_name = name.lower().replace(" ", "_")
        return formatted_name

    @field_validator("title")
    @classmethod
    def __title_default(cls, title, values):
        validated_title = title or values.data["name"]
        return validated_title

    @field_serializer("id", "dataset_id", when_used="unless-none")
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    @field_validator("type", mode="plain")
    @classmethod
    def __validate_type(cls, type, values):
        if type is None:
            return values.data["settings"].type
        return type
