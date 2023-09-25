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

TERMS_METADATA_PROPERTY_MIN_VALUES = 2


class MetadataPropertySchema(BaseModel, ABC):
    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    description: Optional[str] = None
    visible_for_annotators: bool = True
    type: MetadataPropertyTypes = Field(..., allow_mutation=False)

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"type"}

    @abstractproperty
    def server_settings(self) -> Dict[str, Any]:
        return {}

    def to_server_payload(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "visible_for_annotators": self.visible_for_annotators,
            "settings": self.server_settings,
        }


class TermsMetadataProperty(MetadataPropertySchema):
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
        # TODO: add `values` once with now the naming in the backend
        return {"type": self.type, "values": self.values}


class IntegerMetadataProperty(MetadataPropertySchema):
    type: MetadataPropertyTypes = MetadataPropertyTypes.integer
    gt: Optional[int] = None
    lt: Optional[int] = None

    _bounds_validator = root_validator(allow_reuse=True)(validate_numeric_metadata_property_bounds)

    @property
    def server_settings(self) -> Dict[str, Any]:
        # TODO: add `lt` and `gt` once with the naming in the backend
        settings: Dict[str, Any] = {"type": self.type.value}
        if self.gt is not None:
            settings["gt"] = self.gt
        if self.lt is not None:
            settings["lt"] = self.lt
        return settings


class FloatMetadataProperty(MetadataPropertySchema):
    type: MetadataPropertyTypes = MetadataPropertyTypes.float
    gt: Optional[float] = None
    lt: Optional[float] = None

    _bounds_validator = root_validator(allow_reuse=True)(validate_numeric_metadata_property_bounds)

    @property
    def server_settings(self) -> Dict[str, Any]:
        # TODO: add `lt` and `gt` once with the naming in the backend
        settings: Dict[str, Any] = {"type": self.type.value}
        if self.gt is not None:
            settings["gt"] = self.gt
        if self.lt is not None:
            settings["lt"] = self.lt
        return settings
