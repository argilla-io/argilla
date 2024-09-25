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
from typing import Any, Dict, List, Optional, Tuple, Union, Literal
import uuid

from pydantic import BaseModel, Field, field_serializer, field_validator

from argilla._models._record._metadata import MetadataModel, MetadataValue
from argilla._models._record._response import UserResponseModel
from argilla._models._record._suggestion import SuggestionModel
from argilla._models._record._vector import VectorModel
from argilla._models._resource import ResourceModel

__all__ = ["RecordModel", "FieldValue"]


class ChatFieldValue(BaseModel):
    """Schema for the chat field values of a `Record`"""

    role: str
    content: str


CustomFieldValue = dict

FieldValue = Union[List[ChatFieldValue], List[dict], CustomFieldValue, str, None]


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
    def serialize_fields(self, value: Dict[str, FieldValue]) -> Optional[Dict[str, FieldValue]]:
        """Serialize empty fields to None."""
        if isinstance(value, dict) and len(value) == 0:
            return None
        for field_name, field_value in value.items():
            if isinstance(field_value, list) and all(isinstance(chat_field, dict) for chat_field in field_value):
                value[field_name] = [chat_field.model_dump() for chat_field in field_value]
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

    @field_validator("fields", mode="before")
    @classmethod
    def validate_fields(cls, fields: Dict[str, Union[str, None, List[Dict[str, str]]]]) -> Dict[str, FieldValue]:
        """Ensure fields are a dictionary of field names and values."""
        return {field_name: cls._validate_field_value(field_value) for field_name, field_value in fields.items()}

    @classmethod
    def _validate_field_value(cls, field_value: Union[str, None, List[Dict[str, str]]]) -> FieldValue:
        if isinstance(field_value, list):
            if all(isinstance(message, dict) for message in field_value):
                return cls._validate_chat_field(field_value)
            else:
                raise ValueError("Field is not valid. List field values must contain dictionaries.")
        return field_value

    @classmethod
    def _validate_chat_field(cls, chat_field: List[Dict[str, str]]) -> List[ChatFieldValue]:
        validated_chat_field_values = []
        for message in chat_field:
            if "role" not in message or "content" not in message:
                raise ValueError("Chat field values must contain 'role' and 'content' keys.")
            if not all(key in ["role", "content"] for key in message.keys()):
                warnings.warn(
                    "Chat field values should only contain 'role' and 'content' keys. Other keys will be ignored by Argilla."
                )
                message = {key: value for key, value in message.items() if key in ["role", "content"]}
            validated_chat_field_values.append(ChatFieldValue(**message))
        return validated_chat_field_values

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
