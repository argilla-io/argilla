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
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar, Union
from uuid import UUID

from fastapi import Query

from argilla.server.enums import DatasetStatus, FieldType, MetadataPropertyType, SimilarityOrder, SortOrder
from argilla.server.pydantic_v1 import BaseModel, PositiveInt, constr, root_validator
from argilla.server.pydantic_v1 import Field as PydanticField
from argilla.server.pydantic_v1.generics import GenericModel
from argilla.server.schemas.base import UpdateSchema
from argilla.server.schemas.v1.questions import QuestionName
from argilla.server.schemas.v1.records import Record, RecordFilterScope
from argilla.server.schemas.v1.responses import ResponseFilterScope
from argilla.server.search_engine import TextQuery

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

DATASET_NAME_REGEX = r"^(?!-|_)[a-zA-Z0-9-_ ]+$"
DATASET_NAME_MIN_LENGTH = 1
DATASET_NAME_MAX_LENGTH = 200
DATASET_GUIDELINES_MIN_LENGTH = 1
DATASET_GUIDELINES_MAX_LENGTH = 10000

FIELD_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"
FIELD_CREATE_NAME_MIN_LENGTH = 1
FIELD_CREATE_NAME_MAX_LENGTH = 200
FIELD_CREATE_TITLE_MIN_LENGTH = 1
FIELD_CREATE_TITLE_MAX_LENGTH = 500

METADATA_PROPERTY_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"
METADATA_PROPERTY_CREATE_NAME_MIN_LENGTH = 1
METADATA_PROPERTY_CREATE_NAME_MAX_LENGTH = 200
METADATA_PROPERTY_CREATE_TITLE_MIN_LENGTH = 1
METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH = 500

VECTOR_SETTINGS_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"
VECTOR_SETTINGS_CREATE_NAME_MIN_LENGTH = 1
VECTOR_SETTINGS_CREATE_NAME_MAX_LENGTH = 200
VECTOR_SETTINGS_CREATE_TITLE_MIN_LENGTH = 1
VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH = 500

TERMS_METADATA_PROPERTY_VALUES_MIN_ITEMS = 1
TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS = 250

TERMS_FILTER_VALUES_MIN_ITEMS = 1
TERMS_FILTER_VALUES_MAX_ITEMS = 250

FILTERS_AND_MIN_ITEMS = 1
FILTERS_AND_MAX_ITEMS = 50

SEARCH_RECORDS_QUERY_SORT_MIN_ITEMS = 1
SEARCH_RECORDS_QUERY_SORT_MAX_ITEMS = 10


class Dataset(BaseModel):
    id: UUID
    name: str
    guidelines: Optional[str]
    allow_extra_metadata: bool
    status: DatasetStatus
    workspace_id: UUID
    last_activity_at: datetime
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Datasets(BaseModel):
    items: List[Dataset]


DatasetName = Annotated[
    constr(regex=DATASET_NAME_REGEX, min_length=DATASET_NAME_MIN_LENGTH, max_length=DATASET_NAME_MAX_LENGTH),
    PydanticField(..., description="Dataset name"),
]

DatasetGuidelines = Annotated[
    constr(min_length=DATASET_GUIDELINES_MIN_LENGTH, max_length=DATASET_GUIDELINES_MAX_LENGTH),
    PydanticField(..., description="Dataset guidelines"),
]


class DatasetCreate(BaseModel):
    name: DatasetName
    guidelines: Optional[DatasetGuidelines]
    allow_extra_metadata: bool = True
    workspace_id: UUID


class DatasetUpdate(UpdateSchema):
    name: Optional[DatasetName]
    guidelines: Optional[DatasetGuidelines]
    allow_extra_metadata: Optional[bool]

    __non_nullable_fields__ = {"name", "allow_extra_metadata"}


class RecordMetrics(BaseModel):
    count: int


class ResponseMetrics(BaseModel):
    count: int
    submitted: int
    discarded: int
    draft: int


class DatasetMetrics(BaseModel):
    records: RecordMetrics
    responses: ResponseMetrics


class TextFieldSettings(BaseModel):
    type: Literal[FieldType.text]
    use_markdown: bool = False


class Field(BaseModel):
    id: UUID
    name: str
    title: str
    required: bool
    settings: TextFieldSettings
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Fields(BaseModel):
    items: List[Field]


FieldName = Annotated[
    constr(
        regex=FIELD_CREATE_NAME_REGEX,
        min_length=FIELD_CREATE_NAME_MIN_LENGTH,
        max_length=FIELD_CREATE_NAME_MAX_LENGTH,
    ),
    PydanticField(..., description="The name of the field"),
]

FieldTitle = Annotated[
    constr(min_length=FIELD_CREATE_TITLE_MIN_LENGTH, max_length=FIELD_CREATE_TITLE_MAX_LENGTH),
    PydanticField(..., description="The title of the field"),
]


class FieldCreate(BaseModel):
    name: FieldName
    title: FieldTitle
    required: Optional[bool]
    settings: TextFieldSettings


class VectorSettings(BaseModel):
    id: UUID
    name: str
    title: str
    dimensions: int
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

    def check_vector(self, value: List[float]) -> None:
        num_elements = len(value)
        if num_elements != self.dimensions:
            raise ValueError(f"vector must have {self.dimensions} elements, got {num_elements} elements")


class VectorsSettings(BaseModel):
    items: List[VectorSettings]


VectorSettingsTitle = Annotated[
    constr(
        min_length=VECTOR_SETTINGS_CREATE_TITLE_MIN_LENGTH,
        max_length=VECTOR_SETTINGS_CREATE_TITLE_MAX_LENGTH,
    ),
    PydanticField(..., description="The title of the vector settings"),
]


class VectorSettingsCreate(BaseModel):
    name: str = PydanticField(
        ...,
        regex=VECTOR_SETTINGS_CREATE_NAME_REGEX,
        min_length=VECTOR_SETTINGS_CREATE_NAME_MIN_LENGTH,
        max_length=VECTOR_SETTINGS_CREATE_NAME_MAX_LENGTH,
        description="The title of the vector settings",
    )
    title: VectorSettingsTitle
    dimensions: PositiveInt


NT = TypeVar("NT", int, float)


class NumericMetadataProperty(GenericModel, Generic[NT]):
    min: Optional[NT] = None
    max: Optional[NT] = None

    @root_validator(skip_on_failure=True)
    def check_bounds(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        min = values.get("min")
        max = values.get("max")

        if min is not None and max is not None and min >= max:
            raise ValueError(f"'min' ({min}) must be lower than 'max' ({max})")

        return values


class TermsMetadataPropertyCreate(BaseModel):
    type: Literal[MetadataPropertyType.terms]
    values: Optional[List[str]] = PydanticField(
        None, min_items=TERMS_METADATA_PROPERTY_VALUES_MIN_ITEMS, max_items=TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS
    )


class IntegerMetadataPropertyCreate(NumericMetadataProperty[int]):
    type: Literal[MetadataPropertyType.integer]


class FloatMetadataPropertyCreate(NumericMetadataProperty[float]):
    type: Literal[MetadataPropertyType.float]


MetadataPropertyName = Annotated[
    str,
    PydanticField(
        ...,
        regex=METADATA_PROPERTY_CREATE_NAME_REGEX,
        min_length=METADATA_PROPERTY_CREATE_NAME_MIN_LENGTH,
        max_length=METADATA_PROPERTY_CREATE_NAME_MAX_LENGTH,
    ),
]

MetadataPropertyTitle = Annotated[
    constr(min_length=METADATA_PROPERTY_CREATE_TITLE_MIN_LENGTH, max_length=METADATA_PROPERTY_CREATE_TITLE_MAX_LENGTH),
    PydanticField(..., description="The title of the metadata property"),
]

MetadataPropertySettingsCreate = Annotated[
    Union[TermsMetadataPropertyCreate, IntegerMetadataPropertyCreate, FloatMetadataPropertyCreate],
    PydanticField(..., discriminator="type"),
]


class MetadataPropertyCreate(BaseModel):
    name: MetadataPropertyName
    title: MetadataPropertyTitle
    settings: MetadataPropertySettingsCreate
    visible_for_annotators: bool = True


class TermsMetadataProperty(BaseModel):
    type: Literal[MetadataPropertyType.terms]
    values: Optional[List[str]] = None


class IntegerMetadataProperty(BaseModel):
    type: Literal[MetadataPropertyType.integer]
    min: Optional[int] = None
    max: Optional[int] = None


class FloatMetadataProperty(BaseModel):
    type: Literal[MetadataPropertyType.float]
    min: Optional[float] = None
    max: Optional[float] = None


MetadataPropertySettings = Annotated[
    Union[TermsMetadataProperty, IntegerMetadataProperty, FloatMetadataProperty],
    PydanticField(..., discriminator="type"),
]


class MetadataProperty(BaseModel):
    id: UUID
    name: str
    title: str
    settings: MetadataPropertySettings
    visible_for_annotators: bool
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class MetadataProperties(BaseModel):
    items: List[MetadataProperty]


class MetadataParsedQueryParam:
    def __init__(self, string: str):
        k, *v = string.split(":", maxsplit=1)

        self.name: str = k
        self.value: str = "".join(v).strip()


class MetadataQueryParams(BaseModel):
    metadata: List[str] = PydanticField(Query([], pattern=r"^(?=.*[a-z0-9])[a-z0-9_-]+:(.+(,(.+))*)$"))

    @property
    def metadata_parsed(self) -> List[MetadataParsedQueryParam]:
        # TODO: Validate metadata fields names from query params
        return [MetadataParsedQueryParam(q) for q in self.metadata]


class VectorQuery(BaseModel):
    name: str
    record_id: Optional[UUID] = None
    value: Optional[List[float]] = None
    order: SimilarityOrder = SimilarityOrder.most_similar

    @root_validator(skip_on_failure=True)
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


class SuggestionFilterScope(BaseModel):
    entity: Literal["suggestion"]
    question: QuestionName
    property: Optional[Union[Literal["value"], Literal["agent"], Literal["score"]]] = "value"


class MetadataFilterScope(BaseModel):
    entity: Literal["metadata"]
    metadata_property: MetadataPropertyName


FilterScope = Annotated[
    Union[RecordFilterScope, ResponseFilterScope, SuggestionFilterScope, MetadataFilterScope],
    PydanticField(..., discriminator="entity"),
]


class TermsFilter(BaseModel):
    type: Literal["terms"]
    scope: FilterScope
    values: List[str] = PydanticField(
        ..., min_items=TERMS_FILTER_VALUES_MIN_ITEMS, max_items=TERMS_FILTER_VALUES_MAX_ITEMS
    )


class RangeFilter(BaseModel):
    type: Literal["range"]
    scope: FilterScope
    ge: Optional[float]
    le: Optional[float]

    @root_validator(skip_on_failure=True)
    def check_ge_and_le(cls, values: dict) -> dict:
        ge, le = values.get("ge"), values.get("le")

        if ge is None and le is None:
            raise ValueError("At least one of 'ge' or 'le' must be provided")

        if ge is not None and le is not None and ge > le:
            raise ValueError("'ge' must have a value less than or equal to 'le'")

        return values


Filter = Annotated[Union[TermsFilter, RangeFilter], PydanticField(..., discriminator="type")]


class Filters(BaseModel):
    and_: List[Filter] = PydanticField(
        None, alias="and", min_items=FILTERS_AND_MIN_ITEMS, max_items=FILTERS_AND_MAX_ITEMS
    )


class Order(BaseModel):
    scope: FilterScope
    order: SortOrder


class SearchRecordsQuery(BaseModel):
    query: Optional[Query]
    filters: Optional[Filters]
    sort: Optional[List[Order]] = PydanticField(
        None, min_items=SEARCH_RECORDS_QUERY_SORT_MIN_ITEMS, max_items=SEARCH_RECORDS_QUERY_SORT_MAX_ITEMS
    )


class SearchRecord(BaseModel):
    record: Record
    query_score: Optional[float]


class SearchRecordsResult(BaseModel):
    items: List[SearchRecord]
    total: int = 0


class SearchSuggestionOptionsQuestion(BaseModel):
    id: UUID
    name: str


class SearchSuggestionOptions(BaseModel):
    question: SearchSuggestionOptionsQuestion
    agents: List[str]


class SearchSuggestionsOptions(BaseModel):
    items: List[SearchSuggestionOptions]
