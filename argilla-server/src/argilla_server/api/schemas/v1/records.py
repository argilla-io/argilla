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
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from argilla_server.api.schemas.v1.commons import UpdateSchema
from argilla_server.api.schemas.v1.metadata_properties import MetadataPropertyName
from argilla_server.api.schemas.v1.responses import Response, ResponseFilterScope, UserResponseCreate
from argilla_server.api.schemas.v1.suggestions import Suggestion, SuggestionCreate, SuggestionFilterScope
from argilla_server.api.schemas.v1.chat import ChatFieldValue
from argilla_server.enums import RecordInclude, RecordSortField, SimilarityOrder, SortOrder, RecordStatus

# from argilla_server.pydantic_v1 import BaseModel, Field, StrictStr, root_validator, validator
# from argilla_server.pydantic_v1.utils import GetterDict
from pydantic import BaseModel, Field, StrictStr, root_validator, validator

from argilla_server.search_engine import TextQuery
from pydantic import field_validator, model_validator, ConfigDict

RECORDS_CREATE_MIN_ITEMS = 1
RECORDS_CREATE_MAX_ITEMS = 1000

RECORDS_UPDATE_MIN_ITEMS = 1
RECORDS_UPDATE_MAX_ITEMS = 1000

FILTERS_AND_MIN_ITEMS = 1
FILTERS_AND_MAX_ITEMS = 50

TERMS_FILTER_VALUES_MIN_ITEMS = 1
TERMS_FILTER_VALUES_MAX_ITEMS = 250

SEARCH_RECORDS_QUERY_SORT_MIN_ITEMS = 1
SEARCH_RECORDS_QUERY_SORT_MAX_ITEMS = 10

CHAT_FIELDS_MAX_MESSAGES = 500


# TODO: Find an alternative to this on pydantic v2
# class RecordGetterDict(GetterDict):
#     def get(self, key: str, default: Any) -> Any:
#         if key == "metadata":
#             return getattr(self._obj, "metadata_", None)

#         if key == "responses" and not self._obj.is_relationship_loaded("responses"):
#             return default

#         if key == "suggestions" and not self._obj.is_relationship_loaded("suggestions"):
#             return default

#         if key == "vectors":
#             if self._obj.is_relationship_loaded("vectors"):
#                 return {vector.vector_settings.name: vector.value for vector in self._obj.vectors}
#             else:
#                 return default

#         return super().get(key, default)


class Record(BaseModel):
    id: UUID
    status: RecordStatus
    fields: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None
    # TODO: move `responses` to `response` since contextualized endpoint will contains only the user response
    # response: Optional[Response]
    responses: Optional[List[Response]] = None
    suggestions: Optional[List[Suggestion]] = None
    vectors: Optional[Dict[str, List[float]]] = None
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    # TODO[pydantic]: The following keys were removed: `getter_dict`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    # model_config = ConfigDict(from_attributes=True, getter_dict=RecordGetterDict)
    model_config = ConfigDict(from_attributes=True)


class RecordCreate(BaseModel):
    fields: Dict[str, Union[List[ChatFieldValue], StrictStr, None]]
    metadata: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None
    responses: Optional[List[UserResponseCreate]] = None
    suggestions: Optional[List[SuggestionCreate]] = None
    vectors: Optional[Dict[str, List[float]]] = None

    @field_validator("fields")
    @classmethod
    def validate_chat_fields(cls, fields):
        for key, value in fields.items():
            if isinstance(value, list) and all(isinstance(item, ChatFieldValue) for item in value):
                if len(value) > CHAT_FIELDS_MAX_MESSAGES:
                    raise ValueError(
                        f"Number of chat messages in field '{key}' exceeds the maximum allowed value of {CHAT_FIELDS_MAX_MESSAGES}"
                    )

        return fields

    @field_validator("responses")
    @classmethod
    def check_user_id_is_unique(
        cls, responses: Optional[List[UserResponseCreate]]
    ) -> Optional[List[UserResponseCreate]]:
        if responses is None:
            return responses

        user_ids = {}
        for value in responses:
            if user_ids.get(value.user_id):
                raise ValueError(f"'responses' contains several responses for the same user_id={str(value.user_id)!r}")
            user_ids.setdefault(value.user_id, True)

        return responses

    @field_validator("metadata")
    @classmethod
    def prevent_nan_values(cls, metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if metadata is None:
            return metadata

        for k, v in metadata.items():
            if v != v:
                raise ValueError(f"NaN is not allowed as metadata value, found NaN for key {k!r}")

        return metadata


class RecordUpdate(UpdateSchema):
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    suggestions: Optional[List[SuggestionCreate]] = None
    vectors: Optional[Dict[str, List[float]]] = None

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        # Align with the RecordCreate model. Both should have the same name for the metadata field.
        # TODO(@frascuchon): This will be properly adapted once the bulk records refactor is completed.
        return self.metadata_

    @field_validator("metadata_")
    @classmethod
    def prevent_nan_values(cls, metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if metadata is None:
            return metadata

        for k, v in metadata.items():
            if v != v:
                raise ValueError(f"NaN is not allowed as metadata value, found NaN for key {k!r}")

        return {k: v for k, v in metadata.items() if v == v}  # By definition, NaN != NaN


class RecordUpdateWithId(RecordUpdate):
    id: UUID


class RecordUpsert(RecordCreate):
    id: Optional[UUID] = None
    fields: Optional[Dict[str, Union[List[ChatFieldValue], StrictStr, None]]] = None


class RecordIncludeParam(BaseModel):
    relationships: Optional[List[RecordInclude]] = Field(None, alias="keys")
    vectors: Optional[List[str]] = Field(None, alias="vectors")

    @model_validator(mode="before")
    @classmethod
    def check(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        relationships = values.get("relationships")
        if not relationships:
            return values

        vectors = values.get("vectors")
        if vectors is not None and len(vectors) > 0 and RecordInclude.vectors in relationships:
            # TODO: once we have a exception handler for ValueError in v1, remove HTTPException
            # raise ValueError("Cannot include both 'vectors' and 'relationships' in the same request")
            raise ValueError(
                "'include' query param cannot have both 'vectors' and 'vectors:vector_settings_name_1,vectors_settings_name_2,...'",
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
    property: Union[Literal[RecordSortField.inserted_at], Literal[RecordSortField.updated_at], Literal["status"]]


class Records(BaseModel):
    items: List[Record]
    # TODO(@frascuchon): Make it required once fetch records without metadata filter computes also the total
    total: Optional[int] = None


class RecordsCreate(BaseModel):
    items: List[RecordCreate] = Field(..., min_length=RECORDS_CREATE_MIN_ITEMS, max_length=RECORDS_CREATE_MAX_ITEMS)


class RecordsUpdate(BaseModel):
    # TODO: review this definition and align to create model
    items: List[RecordUpdateWithId] = Field(
        ...,
        min_length=RECORDS_UPDATE_MIN_ITEMS,
        max_length=RECORDS_UPDATE_MAX_ITEMS,
    )


class MetadataParsedQueryParam:
    def __init__(self, string: str):
        k, *v = string.split(":", maxsplit=1)

        self.name: str = k
        self.value: str = "".join(v).strip()


class VectorQuery(BaseModel):
    name: str
    record_id: Optional[UUID] = None
    value: Optional[List[float]] = None
    order: SimilarityOrder = SimilarityOrder.most_similar

    @model_validator(mode="before")
    @classmethod
    def check_required(cls, values: dict) -> dict:
        """Check that either 'record_id' or 'value' is provided"""
        record_id = values.get("record_id")
        value = values.get("value")

        if bool(record_id) == bool(value):
            raise ValueError("Either 'record_id' or 'value' must be provided")

        return values


class Query(BaseModel):
    text: Optional[TextQuery] = None
    vector: Optional[VectorQuery] = None


class MetadataFilterScope(BaseModel):
    entity: Literal["metadata"]
    metadata_property: MetadataPropertyName


FilterScope = Annotated[
    Union[RecordFilterScope, ResponseFilterScope, SuggestionFilterScope, MetadataFilterScope],
    Field(..., discriminator="entity"),
]


class Order(BaseModel):
    scope: FilterScope
    order: SortOrder


class TermsFilter(BaseModel):
    type: Literal["terms"]
    scope: FilterScope
    values: List[str] = Field(..., min_length=TERMS_FILTER_VALUES_MIN_ITEMS, max_length=TERMS_FILTER_VALUES_MAX_ITEMS)


class RangeFilter(BaseModel):
    type: Literal["range"]
    scope: FilterScope
    ge: Optional[float]
    le: Optional[float]

    @model_validator(mode="before")
    @classmethod
    def check_ge_and_le(cls, values: dict) -> dict:
        ge, le = values.get("ge"), values.get("le")

        if ge is None and le is None:
            raise ValueError("At least one of 'ge' or 'le' must be provided")

        if ge is not None and le is not None and ge > le:
            raise ValueError("'ge' must have a value less than or equal to 'le'")

        return values


Filter = Annotated[Union[TermsFilter, RangeFilter], Field(..., discriminator="type")]


class Filters(BaseModel):
    and_: List[Filter] = Field(None, alias="and", min_length=FILTERS_AND_MIN_ITEMS, max_length=FILTERS_AND_MAX_ITEMS)


class SearchRecordsQuery(BaseModel):
    query: Optional[Query] = None
    filters: Optional[Filters] = None
    sort: Optional[List[Order]] = Field(
        None,
        min_length=SEARCH_RECORDS_QUERY_SORT_MIN_ITEMS,
        max_length=SEARCH_RECORDS_QUERY_SORT_MAX_ITEMS,
    )


class SearchRecord(BaseModel):
    record: Record
    query_score: Optional[float] = None


class SearchRecordsResult(BaseModel):
    items: List[SearchRecord]
    total: int = 0
