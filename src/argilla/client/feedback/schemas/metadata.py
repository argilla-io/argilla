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

from abc import ABC, abstractproperty
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, Field, root_validator, validator

from argilla.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla.client.feedback.schemas.validators import validate_numeric_metadata_property_bounds

TERMS_METADATA_PROPERTY_MIN_VALUES = 1


class MetadataPropertySchema(BaseModel, ABC):
    """Base schema for the `FeedbackDataset` metadata properties.

    Args:
        name: The name of the metadata property.
        description: A description of the metadata property. Defaults to `None`.
        type: The type of the metadata property. A value should be set for this
            attribute in the class inheriting from this one to be able to use a
            discriminated union based on the `type` field. Defaults to `None`.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one, as they will have the `type` field already defined, and ensured
        to be supported by Argilla.
    """

    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    description: Optional[str] = None
    # TODO: uncomment once the API supports it
    # visible_for_annotators: bool = True
    type: MetadataPropertyTypes = Field(..., allow_mutation=False)

    class Config:
        validate_assignment = True
        extra = Extra.ignore
        exclude = {"type"}

    @abstractproperty
    def server_settings(self) -> Dict[str, Any]:
        return {}

    def to_server_payload(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            # TODO: uncomment once the API supports it
            # "visible_for_annotators": self.visible_for_annotators,
            "settings": self.server_settings,
        }


class TermsMetadataProperty(MetadataPropertySchema):
    """Schema for the `FeedbackDataset` metadata properties of type `terms`. This kind
    of metadata property will be used for filtering the metadata of a record based on
    a list of possible terms or values.

    Args:
        name: The name of the metadata property.
        description: A description of the metadata property. Defaults to `None`.
        values: A list of possible values for the metadata property. It must contain
            at least two values.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import TermsMetadataProperty
        >>> TermsMetadataProperty(name="color", values=["red", "blue", "green"])
    """

    type: MetadataPropertyTypes = MetadataPropertyTypes.terms
    values: List[str] = Field(..., min_items=TERMS_METADATA_PROPERTY_MIN_VALUES)

    @validator("values")
    def check_values(cls, terms_values: List[str], values: Dict[str, Any]) -> List[str]:
        if len(set(terms_values)) != len(terms_values):
            name = values.get("name")
            raise ValueError(f"`TermsMetadataProperty` with name={name} cannot have repeated `values`")
        return terms_values

    @property
    def server_settings(self) -> Dict[str, Any]:
        return {"type": self.type, "values": self.values}


class IntegerMetadataProperty(MetadataPropertySchema):
    """Schema for the `FeedbackDataset` metadata properties of type `integer`. This kind
    of metadata property will be used for filtering the metadata of a record based on
    an integer value to which `gt` and `lt` filters can be applied.

    Args:
        name: The name of the metadata property.
        description: A description of the metadata property. Defaults to `None`.
        min: The lower bound of the integer value. If not provided, then no lower bound
            check will be applied.
        max: The upper bound of the integer value. If not provided, then no upper bound
            check will be applied.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import IntegerMetadataProperty
        >>> IntegerMetadataProperty(name="day", min=0, max=31)
    """

    type: MetadataPropertyTypes = MetadataPropertyTypes.integer
    min: int
    max: int

    _bounds_validator = root_validator(allow_reuse=True)(validate_numeric_metadata_property_bounds)

    @property
    def server_settings(self) -> Dict[str, Any]:
        settings: Dict[str, Any] = {"type": self.type.value}
        if self.min is not None:
            settings["min"] = self.min
        if self.max is not None:
            settings["max"] = self.max
        return settings


class FloatMetadataProperty(MetadataPropertySchema):
    """Schema for the `FeedbackDataset` metadata properties of type `float`. This kind
    of metadata property will be used for filtering the metadata of a record based on
    an float value to which `gt` and `lt` filters can be applied.

    Args:
        name: The name of the metadata property.
        description: A description of the metadata property. Defaults to `None`.
        min: The lower bound of the float value. If not provided, then no lower bound
            check will be applied.
        max: The upper bound of the float value. If not provided, then no upper bound
            check will be applied.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import FloatMetadataProperty
        >>> FloatMetadataProperty(name="price", min=0.0, max=100.0)
    """

    type: MetadataPropertyTypes = MetadataPropertyTypes.float
    min: float
    max: float

    _bounds_validator = root_validator(allow_reuse=True)(validate_numeric_metadata_property_bounds)

    @property
    def server_settings(self) -> Dict[str, Any]:
        settings: Dict[str, Any] = {"type": self.type.value}
        if self.min is not None:
            settings["min"] = self.min
        if self.max is not None:
            settings["max"] = self.max
        return settings
