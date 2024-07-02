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

import warnings
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
from uuid import UUID

from pydantic import BaseModel

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


class AttributeType(str, Enum):
    """Attribute types are the different types of attributes a record can have."""

    FIELD = "field"
    SUGGESTION = "suggestion"
    RESPONSE = "response"
    METADATA = "metadata"
    VECTOR = "vector"
    ID = "id"


class AttributeParameter(BaseModel):
    """Attribute parameters are the different 'sub' values of a records attribute.
    And the source in the data that the parameter is coming from.
    """

    parameter: ParameterType = ParameterType.VALUE
    source: str


class AttributeRoute(BaseModel):
    """AttributeRoute is a representation of a record attribute that is mapped to a source value in the data."""

    source: str
    name: str
    type: Optional[AttributeType] = None
    parameters: List[AttributeParameter] = []

    @property
    def has_value(self) -> bool:
        """All attributes must have a value parameter to be valid."""
        return any(param.parameter == ParameterType.VALUE for param in self.parameters)


class RecordAttributesMap(BaseModel):
    """RecordAttributesMap is a representation of a record attribute mapping that is used to parse data into a record."""

    suggestion: Dict[str, AttributeRoute]
    response: Dict[str, AttributeRoute]
    field: Dict[str, AttributeRoute]
    metadata: Dict[str, AttributeRoute]
    vector: Dict[str, AttributeRoute]
    id: Dict[str, AttributeRoute]


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

        mapping = mapping or {}
        _mapping = self._schematize_mapped_attributes(mapping=mapping)
        _mapping = self._schematize_default_attributes(mapping=_mapping)
        self.mapping: RecordAttributesMap = _mapping

    def __call__(self, data: Dict[str, Any], user_id: Optional[UUID] = None) -> Record:
        """Maps a dictionary of data to a record object.

        Parameters:
            data: A dictionary representing the record.
            user_id: The user id to associate with the record responses.

        Returns:
            Record: The record object.

        """

        record_id = data.get(self.mapping.id["id"].source)
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

    def _schematize_mapped_attributes(self, mapping: Dict[str, Union[str, Sequence[str]]]) -> RecordAttributesMap:
        """Converts a mapping dictionary to a schematized mapping object."""
        schematized_map = {
            "suggestion": {},
            "response": {},
            "field": {},
            "metadata": {},
            "vector": {},
            "id": {},
        }
        for source_key, value in mapping.items():
            mapped_attributes = [value] if isinstance(value, str) else list(value)
            for attribute_mapping in mapped_attributes:
                
                # Split the attribute mapping into its parts based on the '.' delimiter and create an AttributeRoute object.
                attribute_mapping = attribute_mapping.split(".")
                attribute_name = attribute_mapping[0]
                schema_item = self._schema.get(attribute_name)
                type_ = AttributeType(attribute_mapping[1]) if len(attribute_mapping) > 1 else None
                parameter = ParameterType(attribute_mapping[2]) if len(attribute_mapping) > 2 else ParameterType.VALUE
                attribute_route = AttributeRoute(
                    source=source_key,
                    name=attribute_name,
                    type=type_,
                    parameters=[AttributeParameter(parameter=parameter, source=source_key)],
                )
                attribute_route = self._select_attribute_type(attribute=attribute_route, schema_item=schema_item)
                
                # Add the attribute route to the schematized map based on the attribute type.
                if attribute_route.name in schematized_map[attribute_route.type]:
                    # Some attributes may be mapped to multiple source values, so we need to append the parameters.
                    schematized_map[attribute_route.type][attribute_route.name].parameters.extend(
                        attribute_route.parameters
                    )
                else:
                    schematized_map[attribute_route.type][attribute_route.name] = attribute_route

        return RecordAttributesMap(**schematized_map)

    def _select_attribute_type(self, attribute, schema_item: Optional[object] = None):
        """Selects the attribute type based on the schema item and the attribute type. 
           This method implements the logic to infer the attribute type based on the schema item if the attribute type is not provided.
           If the attribute type is not provided, it will be inferred based on the schema item.
        """
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

    def _schematize_default_attributes(self, mapping: RecordAttributesMap) -> RecordAttributesMap:
        """ Updates the mapping with default attributes that are not provided in the mapping.
            Uses the schema of the dataset to infer the default attributes and add them to the mapping.
            
            Parameters:
                mapping: The mapping object to update with default attributes.
            
            Returns:
                RecordAttributesMap: The updated mapping object.
        """

        if len(mapping.id) == 0:
            # If the id is not provided in the mapping, we will map the 'id' key to the 'id' attribute.
            mapping.id["id"] = AttributeRoute(source="id", name="id", type=AttributeType.ID)
            
        # Map keys that match question names to the suggestion attribute type.
        for question in self._dataset.settings.questions:
            if question.name not in mapping.suggestion:
                mapping.suggestion[question.name] = AttributeRoute(
                    source=question.name,
                    name=question.name,
                    type=AttributeType.SUGGESTION,
                    parameters=[AttributeParameter(source=question.name)],
                )

            elif not mapping.suggestion[question.name].has_value:
                mapping.suggestion[question.name].parameters.append(AttributeParameter(source=question.name))

        for field in self._dataset.settings.fields:
            if field.name not in mapping.field:
                mapping.field[field.name] = AttributeRoute(
                    source=field.name,
                    name=field.name,
                    type=AttributeType.FIELD,
                )

        for metadata in self._dataset.settings.metadata:
            if metadata.name not in mapping.metadata:
                mapping.metadata[metadata.name] = AttributeRoute(
                    source=metadata.name,
                    name=metadata.name,
                    type=AttributeType.METADATA,
                )

        for vector in self._dataset.settings.vectors:
            if vector.name not in mapping.vector:
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
            parameters = {param.parameter: data.get(param.source) for param in route.parameters}
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
