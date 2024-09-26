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

from typing import List, Any, Union, Literal, Annotated

from pydantic import BaseModel, Field


class RecordFilterScopeModel(BaseModel):
    entity: Literal["record"] = "record"
    property: Literal["status", "inserted_at", "updated_at"] = "status"


class ResponseFilterScopeModel(BaseModel):
    """Filter scope for filtering on a response entity."""

    entity: Literal["response"] = "response"
    question: Union[str, None] = None
    property: Union[Literal["status"], None] = None


class SuggestionFilterScopeModel(BaseModel):
    """Filter scope for filtering on a suggestion entity."""

    entity: Literal["suggestion"] = "suggestion"
    question: str
    property: Union[Literal["value"], Literal["agent"], Literal["score"], None] = "value"


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
    values: List[str]
    scope: ScopeModel


class RangeFilterModel(BaseModel):
    """Filter model for range filter."""

    type: Literal["range"] = "range"
    ge: Union[Any, None] = None
    le: Union[Any, None] = None
    scope: ScopeModel


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


class QueryModel(BaseModel):
    """Query part of the search query model"""

    text: TextQueryModel


class SearchQueryModel(BaseModel):
    """The main search query model."""

    query: Union[QueryModel, None] = None
    filters: Union[AndFilterModel, None] = None
