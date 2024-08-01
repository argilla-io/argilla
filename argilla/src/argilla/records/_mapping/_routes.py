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
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ParameterType(str, Enum):
    """Parameter types are the different 'sub' values of a records attribute.
    For example, the value, score, or agent of a suggestion."""

    VALUE = "value"
    SCORE = "score"
    AGENT = "agent"

    @classmethod
    def values(cls) -> List[str]:
        return [param.value for param in cls]


class AttributeType(str, Enum):
    """Attribute types are the different types of attributes a record can have."""

    FIELD = "field"
    SUGGESTION = "suggestion"
    RESPONSE = "response"
    METADATA = "metadata"
    VECTOR = "vector"
    ID = "id"

    @classmethod
    def values(cls) -> List[str]:
        return [attr.value for attr in cls]


class AttributeParameter(BaseModel):
    """Attribute parameters are reference connections between the `ParameterType`'s of a records `AttributeType`.
    The connect the source key to the sub value of the attribute. i.e. column name 'score' to the 'score' of a suggestion.
    """

    parameter_type: ParameterType = ParameterType.VALUE
    source: str


class AttributeRoute(BaseModel):
    """AttributeRoute is a reference connection between a record's attribute and a source value in the data.
    It connects the source key with the attribute name and type. For example, connecting the columns 'score'
    and 'y' to the 'score' and 'value' of a suggestion.
    """

    source: str
    name: str
    type: Optional[AttributeType] = None
    parameters: List[AttributeParameter] = []

    def set_parameter(self, parameter: AttributeParameter):
        """Set a parameter for the route.
        An existing parameter with same parameter type will be replaced by this new one.
        """
        for p in self.parameters:
            if p.parameter_type == parameter.parameter_type:
                self.parameters.remove(p)
                break
        self.parameters.append(parameter)


class RecordAttributesMap(BaseModel):
    """RecordAttributesMap is a representation of a record attribute mapping that is used to parse data into a record."""

    suggestion: Dict[str, AttributeRoute] = Field(default_factory=dict)
    response: Dict[str, AttributeRoute] = Field(default_factory=dict)
    field: Dict[str, AttributeRoute] = Field(default_factory=dict)
    metadata: Dict[str, AttributeRoute] = Field(default_factory=dict)
    vector: Dict[str, AttributeRoute] = Field(default_factory=dict)

    id: AttributeRoute = AttributeRoute(source="id", name="id", type=AttributeType.ID)

    def _get_routes_group_by_type(self, type: AttributeType):
        """Utility method to facilitate getting the routes by type."""
        return {
            AttributeType.SUGGESTION: self.suggestion,
            AttributeType.RESPONSE: self.response,
            AttributeType.FIELD: self.field,
            AttributeType.METADATA: self.metadata,
            AttributeType.VECTOR: self.vector,
            AttributeType.ID: self.id,
        }[type]

    def get_by_name_and_type(self, name: str, type: AttributeType) -> Optional[AttributeRoute]:
        """Utility method to get a route by name and type"""
        if name == "id" and AttributeType.ID:
            return self.id
        return self._get_routes_group_by_type(type).get(name)

    def add_route(self, attribute_route: AttributeRoute) -> None:
        """Utility method to get a new mapping route"""
        if attribute_route.type == AttributeType.ID:
            self.id = attribute_route
        else:
            self._get_routes_group_by_type(attribute_route.type)[attribute_route.name] = attribute_route

    def keys(self) -> List[str]:
        """Utility method to get all the keys in the mapping"""
        return (
            list(self.suggestion.keys())
            + list(self.response.keys())
            + list(self.field.keys())
            + list(self.metadata.keys())
            + list(self.vector.keys())
            + ["id"]
        )
