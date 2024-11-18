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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union, Tuple
from uuid import UUID
import warnings

from argilla._exceptions import RecordsIngestionError
from argilla.records._resource import Record
from argilla.responses import Response
from argilla.settings import FieldBase, VectorField
from argilla.settings._metadata import MetadataPropertyBase
from argilla.settings._question import QuestionPropertyBase
from argilla.suggestions import Suggestion
from argilla.records._mapping._routes import (
    AttributeRoute,
    RecordAttributesMap,
    AttributeType,
    ParameterType,
    AttributeParameter,
)

if TYPE_CHECKING:
    from argilla.datasets import Dataset


class IngestedRecordMapper:
    """IngestedRecordMapper is a class that is used to map data into a record object.
    It maps values in ingested data to the appropriate record attributes, based on the user
    provided mapping and the schema of the dataset.

    The Mapper builds and uses a `RecordAttributesMap` object to map the data to the appropriate record attributes.

    Attributes:
        dataset: The dataset the record will be added to.
        mapping: A dictionary mapping from source data keys/ columns to Argilla fields, questions, ids, etc.
        user_id: The user id to associate with the record responses.
    """

    mapping: RecordAttributesMap = None

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
        default_mapping = self._schematize_default_attributes()
        self.mapping = self._schematize_mapped_attributes(mapping=mapping, default_mapping=default_mapping)

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

        unknown_keys = [key for key in data.keys() if key not in self.mapping.keys()]
        if unknown_keys:
            warnings.warn(f"Keys {unknown_keys} in data are not present in the mapping and will be ignored.")

        if len([k for k in data if k != self.mapping.id.source]) == 0:
            raise RecordsIngestionError(
                message=f"Record has no data. All records must have at least one attribute. Record id: {record_id}."
            )

        if data and not (record_id or suggestions or responses or fields or metadata or vectors):
            raise RecordsIngestionError(
                message=f"""Record has no identifiable keys. If keys in source dataset
                do not match the names in `dataset.settings`, you should use a
                `mapping` with `dataset.records.log`.
                Available keys: {self.mapping.keys()}.
                Unkown keys: {unknown_keys}. """
            )

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
            for attr_mapping in mapped_attributes:
                attr_name, attr_type, parameter = self._parse_dot_notation(attr_mapping)

                attr_type = AttributeType(attr_type or AttributeType.SUGGESTION)
                parameter = AttributeParameter(parameter_type=parameter or ParameterType.VALUE, source=source_key)

                attr_route = default_mapping.get_by_name_and_type(name=attr_name, type=attr_type)
                if attr_route:
                    attr_route.source = source_key
                    attr_route.set_parameter(parameter)
                else:
                    attr_route = AttributeRoute(
                        name=attr_name,
                        source=source_key,
                        type=attr_type,
                        parameters=[parameter],
                    )
                    attr_route = self._select_attribute_type(attribute_route=attr_route)
                    default_mapping.add_route(attr_route)

        return default_mapping

    def _parse_dot_notation(self, attribute_mapping: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Parses a string in the format of 'attribute.type.parameter' into its attribute parts parts using regex."""

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
        attr_name, type_, parameter = match.groups()
        return attr_name, type_, parameter

    def _select_attribute_type(self, attribute_route: AttributeRoute) -> AttributeRoute:
        """Selects the attribute type based on the schema item and the attribute type.
        This method implements the logic to infer the attribute type based on the schema item if the attribute type is not provided.
        If the attribute type is not provided, it will be inferred based on the schema item.
        """
        schema_item = self._schema.get(attribute_route.name)
        if isinstance(schema_item, QuestionPropertyBase) and (
            attribute_route.type is None or attribute_route.type == AttributeType.SUGGESTION
        ):
            # Suggestions are the default destination for questions.
            attribute_route.type = AttributeType.SUGGESTION
        elif isinstance(schema_item, QuestionPropertyBase) and attribute_route.type == AttributeType.RESPONSE:
            attribute_route.type = AttributeType.RESPONSE
        elif isinstance(schema_item, FieldBase):
            attribute_route.type = AttributeType.FIELD
        elif isinstance(schema_item, VectorField):
            attribute_route.type = AttributeType.VECTOR
        elif isinstance(schema_item, MetadataPropertyBase):
            attribute_route.type = AttributeType.METADATA
        elif attribute_route.name == "id":
            attribute_route.type = AttributeType.ID
        else:
            raise RecordsIngestionError(f"Mapped attribute is not a valid dataset attribute: {attribute_route.name}.")
        return attribute_route

    def _schematize_default_attributes(self) -> RecordAttributesMap:
        """Creates the mapping with default attribute routes. Uses the schema of the dataset to determine
         the default attributes and add them to the mapping with their names as keys. This means that
         keys in the data that match the names of dataset attributes will be mapped to them by default.

        Returns:
            RecordAttributesMap: The mapping object.
        """
        mapping = RecordAttributesMap()

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
            if parameters.get(ParameterType.VALUE) is None:
                continue
            question = self._dataset.questions[name]
            suggestion = Suggestion(
                **parameters,
                question_name=question.name,
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
            value = data.get(route.source)
            if value is None:
                continue
            response = Response(
                value=value,
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
            if value is None:
                continue
            attributes[name] = value

        return attributes
