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

import re
import warnings
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union, Tuple
from uuid import UUID

from pydantic import BaseModel, Field

from argilla.records._resource import Record
from argilla.responses import Response
from argilla.settings import TextField, VectorField
from argilla.settings._metadata import MetadataPropertyBase
from argilla.settings._question import QuestionPropertyBase
from argilla.suggestions import Suggestion

if TYPE_CHECKING:
    from argilla.datasets import Dataset


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
    """Attribute parameters are the different 'sub' values of a records attribute.
    And the source in the data that the parameter is coming from.
    """

    parameter_type: ParameterType = ParameterType.VALUE
    source: str


class AttributeRoute(BaseModel):
    """AttributeRoute is a representation of a record attribute that is mapped to a source value in the data."""

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
        return {
            AttributeType.SUGGESTION: self.suggestion,
            AttributeType.RESPONSE: self.response,
            AttributeType.FIELD: self.field,
            AttributeType.METADATA: self.metadata,
            AttributeType.VECTOR: self.vector,
            AttributeType.ID: self.id,
        }[type]

    def get_by_name_and_type(self, name: str, type: AttributeType) -> Optional[AttributeRoute]:
        """Get a route by name and type"""
        if name == "id" and AttributeType.ID:
            return self.id
        return self._get_routes_group_by_type(type).get(name)

    def add_route(self, attribute_route: AttributeRoute) -> None:
        """Ad a new mapping route"""
        if attribute_route.type == AttributeType.ID:
            self.id = attribute_route
        else:
            self._get_routes_group_by_type(attribute_route.type)[attribute_route.name] = attribute_route


class IngestedRecordMapper:
    """IngestedRecordMapper is a class that is used to map data into a record object.
    It maps values in ingested data to the appropriate record attributes, based on the user provided mapping and the schema of the dataset.

    Attributes:
        dataset: The dataset the record will be added to.
        mapping: A dictionary mapping from source data keys/ columns to Argilla fields, questions, ids, etc.
        user_id: The user id to associate with the record responses.
    """

    def __init__(
        self,
        dataset: "Dataset",
        user_id: UUID,
        mapping: Optional[Dict[str, Union[str, Sequence[str]]]] = None,
    ):
        self._dataset = dataset
        self._schema = dataset.schema
        self.user_id = user_id

        default_mapping = self._schematize_default_attributes()
        self.mapping = self._schematize_mapped_attributes(mapping=mapping or {}, default_mapping=default_mapping)

    def __call__(self, data: Dict[str, Any], user_id: Optional[UUID] = None) -> Record:
        """Maps a dictionary of data to a record object.

        Parameters:
            data: A dictionary representing the record.
            user_id: The user id to associate with the record responses.

        Returns:
            Record: The record object.

        """

        record_id = data.get(self.mapping.id.source)
        suggestions = self._map_suggestions(data=data, mapping=self.mapping.suggestion)
        responses = self._map_responses(data=data, user_id=user_id or self.user_id, mapping=self.mapping.response)
        fields = self._map_attributes(data=data, mapping=self.mapping.field)
        metadata = self._map_attributes(data=data, mapping=self.mapping.metadata)
        vectors = self._map_attributes(data=data, mapping=self.mapping.vector)

        return Record(
            id=record_id,
            fields=fields,
            vectors=vectors,
            metadata=metadata,
            suggestions=suggestions,
            responses=responses,
            _dataset=self._dataset,
        )

    ##########################################
    # Private helper functions - Build Mapping
    ##########################################

    def _schematize_mapped_attributes(
        self,
        mapping: Dict[str, Union[str, Sequence[str]]],
        default_mapping: RecordAttributesMap,
    ) -> RecordAttributesMap:
        """Extends the default mapping with a schematized mapping object provided from a dict"""

        for source_key, value in mapping.items():
            mapped_attributes = [value] if isinstance(value, str) else list(value)
            for attribute_mapping in mapped_attributes:
                attribute_name, attr_type, parameter = self._parse_dot_notation(attribute_mapping)

                attr_type = AttributeType(attr_type or AttributeType.SUGGESTION)
                parameter = AttributeParameter(parameter_type=parameter or ParameterType.VALUE, source=source_key)

                attribute_route = default_mapping.get_by_name_and_type(name=attribute_name, type=attr_type)
                if attribute_route:
                    attribute_route.source = source_key
                    attribute_route.set_parameter(parameter)
                else:
                    attribute_route = AttributeRoute(
                        name=attribute_name,
                        source=source_key,
                        type=attr_type,
                        parameters=[parameter],
                    )
                    attribute_route = self._select_attribute_type(attribute=attribute_route)
                    default_mapping.add_route(attribute_route)

        return default_mapping

    def _parse_dot_notation(self, attribute_mapping: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Parses a string in the format of 'attribute.type.parameter' into its parts using regex."""

        available_attributes = list(self._schema.keys()) + ["id"]
        available_parameters = ParameterType.values()
        available_types = AttributeType.values()

        # The pattern is in the format of 'attribute[.type[.parameter]]' where type and parameter are optional.
        pattern = re.compile(
            rf"^({'|'.join(available_attributes)})"
            rf"(?:\.({'|'.join(available_types)}))?"
            rf"(?:\.({'|'.join(available_parameters)}))?$"
        )

        match = pattern.match(attribute_mapping)
        if not match:
            raise ValueError(
                f"Invalid attribute mapping format: {attribute_mapping}. "
                "Attribute mapping must be in the format of 'attribute[.type[.parameter]]'."
                f"Available attributes: {available_attributes}, types: {available_types}, parameters: {available_parameters}."
            )
        attribute_name, type_, parameter = match.groups()
        return attribute_name, type_, parameter

    def _select_attribute_type(self, attribute: AttributeRoute) -> AttributeRoute:
        """Selects the attribute type based on the schema item and the attribute type.
        This method implements the logic to infer the attribute type based on the schema item if the attribute type is not provided.
        If the attribute type is not provided, it will be inferred based on the schema item.
        """
        schema_item = self._schema.get(attribute.name)
        if isinstance(schema_item, QuestionPropertyBase) and (
            attribute.type is None or attribute.type == AttributeType.SUGGESTION
        ):
            # Suggestions are the default destination for questions.
            attribute.type = AttributeType.SUGGESTION
        elif isinstance(schema_item, QuestionPropertyBase) and attribute.type == AttributeType.RESPONSE:
            attribute.type = AttributeType.RESPONSE
        elif isinstance(schema_item, TextField):
            attribute.type = AttributeType.FIELD
        elif isinstance(schema_item, VectorField):
            attribute.type = AttributeType.VECTOR
        elif isinstance(schema_item, MetadataPropertyBase):
            attribute.type = AttributeType.METADATA
        elif attribute.name == "id":
            attribute.type = AttributeType.ID
        else:
            warnings.warn(message=f"Record attribute {attribute.name} is not in the schema or mapping so skipping.")
        return attribute

    def _schematize_default_attributes(self) -> RecordAttributesMap:
        """Creates the mapping with default attributes. Uses the schema of the dataset to infer
         the default attributes and add them to the mapping.

        Returns:
            RecordAttributesMap: The mapping object.
        """
        mapping = RecordAttributesMap()

        # Map keys that match question names to the suggestion attribute type.
        for question in self._dataset.settings.questions:
            mapping.suggestion[question.name] = AttributeRoute(
                source=question.name,
                name=question.name,
                type=AttributeType.SUGGESTION,
                parameters=[AttributeParameter(source=question.name)],
            )

        for field in self._dataset.settings.fields:
            mapping.field[field.name] = AttributeRoute(
                source=field.name,
                name=field.name,
                type=AttributeType.FIELD,
            )

        for metadata in self._dataset.settings.metadata:
            mapping.metadata[metadata.name] = AttributeRoute(
                source=metadata.name,
                name=metadata.name,
                type=AttributeType.METADATA,
            )

        for vector in self._dataset.settings.vectors:
            mapping.vector[vector.name] = AttributeRoute(
                source=vector.name,
                name=vector.name,
                type=AttributeType.VECTOR,
            )

        return mapping

    ##########################################
    # Private helper functions - Parse Records
    ##########################################

    def _map_suggestions(self, data: Dict[str, Any], mapping) -> List[Suggestion]:
        """Converts an arbitrary dictionary to a list of Suggestion objects for use by the add or update methods.
        Suggestions can be defined accross multiple columns in the data, so we need to map them to the appropriately.add()

        Parameters:
            data: A dictionary representing the vector.
            mapping: A dictionary mapping from source data keys/ columns to Argilla fields, questions, ids, etc.

        Returns:
             A list of Suggestion objects.

        """
        suggestions = []

        for name, route in mapping.items():
            if route.source not in data:
                continue
            parameters = {param.parameter_type: data.get(param.source) for param in route.parameters}
            schema_item = self._dataset.schema.get(name)
            suggestion = Suggestion(
                **parameters,
                question_name=route.name,
                question_id=schema_item.id,
            )
            suggestions.append(suggestion)

        return suggestions

    def _map_responses(self, data: Dict[str, Any], user_id: UUID, mapping) -> List[Response]:
        """Converts an arbitrary dictionary to a list of Response objects for use by the add or update methods.

        Parameters:
             data: A dictionary representing the vector.
             mapping: A dictionary mapping from source data keys/ columns to Argilla fields, questions, ids, etc.
             user_id: The user id to associate with the record responses.

        Returns:
             A list of Response objects.
        """
        responses = []

        for name, route in mapping.items():
            response = Response(
                value=data.get(route.source),
                question_name=name,
                user_id=user_id,
            )
            responses.append(response)

        return responses

    def _map_attributes(self, data: Dict[str, Any], mapping: Dict[str, AttributeRoute]) -> Dict[str, Any]:
        """Converts a dictionary to a dictionary of attributes for use by the add or update methods."""
        attributes = {}
        for name, route in mapping.items():
            if route.source not in data:
                continue
            value = data.get(route.source)
            if value is not None:
                attributes[name] = value
        return attributes
