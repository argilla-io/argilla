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

import uuid
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from pydantic import Field, field_serializer, field_validator

from argilla._models._record._metadata import MetadataModel, MetadataValue
from argilla._models._record._response import UserResponseModel
from argilla._models._record._suggestion import SuggestionModel
from argilla._models._record._vector import VectorModel
from argilla._models._resource import ResourceModel

__all__ = ["RecordModel", "FieldValue"]

FieldValue = Union[str, None]


class RecordModel(ResourceModel):
    """Schema for the records of a `Dataset`"""

    status: Literal["pending", "completed"] = "pending"
    fields: Optional[Dict[str, FieldValue]] = None
    metadata: Optional[Union[List[MetadataModel], Dict[str, MetadataValue]]] = Field(default_factory=dict)
    vectors: Optional[List[VectorModel]] = Field(default_factory=list)
    responses: Optional[List[UserResponseModel]] = Field(default_factory=list)
    suggestions: Optional[Union[Tuple[SuggestionModel], List[SuggestionModel]]] = Field(default_factory=tuple)
    external_id: Optional[Any] = Field(default=None)

    @field_serializer("external_id", when_used="unless-none")
    def serialize_external_id(self, value: str) -> str:
        return str(value)

    @field_serializer("vectors", when_used="unless-none")
    def serialize_vectors(self, value: List[VectorModel]) -> Dict[str, List[float]]:
        dumped_vectors = [vector.model_dump() for vector in value]
        return {vector["name"]: vector["vector_values"] for vector in dumped_vectors}

    @field_serializer("metadata", when_used="unless-none")
    def serialize_metadata(self, value: List[MetadataModel]) -> Dict[str, Any]:
        """Serialize metadata to a dictionary of key-value pairs based on the metadata name and value."""
        return {metadata.name: metadata.value for metadata in value}

    @field_serializer("fields", when_used="always")
    def serialize_empty_fields(self, value: Dict[str, Union[str, None]]) -> Optional[Dict[str, Union[str, None]]]:
        """Serialize empty fields to None."""
        if isinstance(value, dict) and len(value) == 0:
            return None
        return value

    @field_validator("metadata", mode="before")
    @classmethod
    def validate_metadata(cls, metadata: Union[List[MetadataModel], dict]) -> List[MetadataModel]:
        """Ensure metadata is a list of MetadataModel instances when provided as a dict."""
        if not metadata:
            return []
        if isinstance(metadata, dict):
            return [MetadataModel(name=key, value=value) for key, value in metadata.items()]
        return metadata

    @field_validator("external_id", mode="before")
    @classmethod
    def validate_external_id(cls, external_id: Any) -> Union[str, int, uuid.UUID]:
        """Ensure external_id is captured correctly and only converted if None."""
        if external_id is None:
            external_id = uuid.uuid4()
        return external_id

    @field_validator("vectors", mode="before")
    @classmethod
    def empty_vectors_if_none(cls, vectors: Optional[List[VectorModel]]) -> Optional[List[VectorModel]]:
        """Ensure vectors is None if not provided."""
        if vectors is None:
            return []
        return vectors

    @field_validator("responses", mode="before")
    @classmethod
    def empty_responses_if_none(cls, responses: Optional[List[UserResponseModel]]) -> Optional[List[UserResponseModel]]:
        """Ensure responses is None if not provided."""
        if responses is None:
            return []
        return responses

    @field_validator("suggestions", mode="before")
    @classmethod
    def empty_suggestions_if_none(
        cls, suggestions: Optional[Union[Tuple[SuggestionModel], List[SuggestionModel]]]
    ) -> Optional[Union[Tuple[SuggestionModel], List[SuggestionModel]]]:
        """Ensure suggestions is None if not provided."""
        if suggestions is None:
            return []
        return suggestions
