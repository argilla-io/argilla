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
from datetime import datetime
from typing import List, Any, Union, Literal, Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class RecordFilterScopeModel(BaseModel):
    entity: Literal["record"] = "record"
    property: Literal["id", "external_id", "inserted_at", "updated_at", "status"] = "status"


class ResponseFilterScopeModel(BaseModel):
    """Filter scope for filtering on a response entity."""

    entity: Literal["response"] = "response"
    question: Union[str, None] = None
    property: Union[Literal["status"], None] = None


class SuggestionFilterScopeModel(BaseModel):
    """Filter scope for filtering on a suggestion entity."""

    entity: Literal["suggestion"] = "suggestion"
    question: str
    property: Union[Literal["value", "agent", "score", "type"], None] = "value"


class MetadataFilterScopeModel(BaseModel):
    """Filter scope for filtering on a metadata entity."""

    entity: Literal["metadata"] = "metadata"
    metadata_property: str


ScopeModel = Annotated[
    Union[
        RecordFilterScopeModel,
        ResponseFilterScopeModel,
        SuggestionFilterScopeModel,
        MetadataFilterScopeModel,
    ],
    Field(discriminator="entity"),
]


class TermsFilterModel(BaseModel):
    """Filter model for terms filter."""

    type: Literal["terms"] = "terms"
    values: List[Any]
    scope: ScopeModel

    @field_serializer("values", when_used="unless-none")
    def serialize_values(self, values):
        sanitized_values = []
        for value in values:
            if isinstance(value, UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            sanitized_values.append(value)

        return sanitized_values


class RangeFilterModel(BaseModel):
    """Filter model for range filter."""

    type: Literal["range"] = "range"
    ge: Union[Any, None] = None
    le: Union[Any, None] = None
    scope: ScopeModel

    @field_serializer("ge", "le", when_used="unless-none")
    def serialize_values(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value


FilterModel = Annotated[
    Union[
        TermsFilterModel,
        RangeFilterModel,
    ],
    Field(discriminator="type"),
]


class AndFilterModel(BaseModel):
    """And filter model."""

    type: Literal["and"] = "and"

    and_: List["FilterModel"] = Field(alias="and")


class TextQueryModel(BaseModel):
    """Text query model."""

    q: str
    field: Union[str, None] = None


class VectorQueryModel(BaseModel):
    name: str
    record_id: Optional[UUID] = None
    value: Optional[List[float]] = None
    order: Literal["most_similar", "least_similar"] = "most_similar"

    @field_serializer("record_id", when_used="unless-none", return_type=str)
    def serialize_record_id(self, value):
        return str(value)


class QueryModel(BaseModel):
    """Query part of the search query model"""

    text: Union[TextQueryModel, None] = None
    vector: Union[VectorQueryModel, None] = None


class SearchQueryModel(BaseModel):
    """The main search query model."""

    query: Union[QueryModel, None] = None
    filters: Union[AndFilterModel, None] = None
