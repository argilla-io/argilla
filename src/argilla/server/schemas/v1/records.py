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

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from fastapi import HTTPException

from argilla.server.enums import RecordInclude, RecordSortField
from argilla.server.pydantic_v1 import BaseModel, Field, root_validator, validator
from argilla.server.pydantic_v1.utils import GetterDict
from argilla.server.schemas.base import UpdateSchema
from argilla.server.schemas.v1.responses import Response, UserResponseCreate
from argilla.server.schemas.v1.suggestions import Suggestion, SuggestionCreate

RECORDS_CREATE_MIN_ITEMS = 1
RECORDS_CREATE_MAX_ITEMS = 1000

RECORDS_UPDATE_MIN_ITEMS = 1
RECORDS_UPDATE_MAX_ITEMS = 1000


class RecordGetterDict(GetterDict):
    def get(self, key: str, default: Any) -> Any:
        if key == "metadata":
            return getattr(self._obj, "metadata_", None)

        if key == "responses" and not self._obj.is_relationship_loaded("responses"):
            return default

        if key == "suggestions" and not self._obj.is_relationship_loaded("suggestions"):
            return default

        if key == "vectors":
            if self._obj.is_relationship_loaded("vectors"):
                return {vector.vector_settings.name: vector.value for vector in self._obj.vectors}
            else:
                return default

        return super().get(key, default)


class Record(BaseModel):
    id: UUID
    fields: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    external_id: Optional[str]
    # TODO: move `responses` to `response` since contextualized endpoint will contains only the user response
    # response: Optional[Response]
    responses: Optional[List[Response]]
    suggestions: Optional[List[Suggestion]]
    vectors: Optional[Dict[str, List[float]]]
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        getter_dict = RecordGetterDict


class RecordCreate(BaseModel):
    fields: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    external_id: Optional[str]
    responses: Optional[List[UserResponseCreate]]
    suggestions: Optional[List[SuggestionCreate]]
    vectors: Optional[Dict[str, List[float]]]

    @validator("responses")
    def check_user_id_is_unique(cls, values: Optional[List[UserResponseCreate]]) -> Optional[List[UserResponseCreate]]:
        if values is None:
            return values

        user_ids = []
        for value in values:
            if value.user_id in user_ids:
                raise ValueError(f"'responses' contains several responses for the same user_id={str(value.user_id)!r}")
            user_ids.append(value.user_id)

        return values


class RecordUpdate(UpdateSchema):
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    suggestions: Optional[List[SuggestionCreate]] = None
    vectors: Optional[Dict[str, List[float]]]


class RecordUpdateWithId(RecordUpdate):
    id: UUID


class RecordIncludeParam(BaseModel):
    relationships: Optional[List[RecordInclude]] = Field(None, alias="keys")
    vectors: Optional[List[str]] = Field(None, alias="vectors")

    @root_validator(skip_on_failure=True)
    def check(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        relationships = values.get("relationships")
        if not relationships:
            return values

        vectors = values.get("vectors")
        if vectors is not None and len(vectors) > 0 and RecordInclude.vectors in relationships:
            # TODO: once we have a exception handler for ValueError in v1, remove HTTPException
            # raise ValueError("Cannot include both 'vectors' and 'relationships' in the same request")
            raise ValueError("'include' query param cannot have both 'vectors' and 'vectors:vector_settings_name_1,vectors_settings_name_2,...'",
            )

        return values

    @property
    def with_responses(self) -> bool:
        return self._has_relationships and RecordInclude.responses in self.relationships

    @property
    def with_suggestions(self) -> bool:
        return self._has_relationships and RecordInclude.suggestions in self.relationships

    @property
    def with_all_vectors(self) -> bool:
        return self._has_relationships and not self.vectors and RecordInclude.vectors in self.relationships

    @property
    def with_some_vector(self) -> bool:
        return self.vectors is not None and len(self.vectors) > 0

    @property
    def _has_relationships(self):
        return self.relationships is not None


class RecordFilterScope(BaseModel):
    entity: Literal["record"]
    property: Union[Literal[RecordSortField.inserted_at], Literal[RecordSortField.updated_at]]


class Records(BaseModel):
    items: List[Record]
    # TODO(@frascuchon): Make it required once fetch records without metadata filter computes also the total
    total: Optional[int] = None


class RecordsCreate(BaseModel):
    items: List[RecordCreate] = Field(..., min_items=RECORDS_CREATE_MIN_ITEMS, max_items=RECORDS_CREATE_MAX_ITEMS)


class RecordsUpdate(BaseModel):
    # TODO: review this definition and align to create model
    items: List[RecordUpdateWithId] = Field(..., min_items=RECORDS_UPDATE_MIN_ITEMS, max_items=RECORDS_UPDATE_MAX_ITEMS)
