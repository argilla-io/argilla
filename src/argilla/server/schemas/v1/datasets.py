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

from fastapi import HTTPException, Query
from pydantic import BaseModel, PositiveInt, conlist, constr, root_validator, validator
from pydantic import Field as PydanticField
from pydantic.generics import GenericModel
from pydantic.utils import GetterDict

from argilla.server.enums import RecordInclude, RecordSortField, SimilarityOrder, SortOrder
from argilla.server.schemas.base import UpdateSchema
from argilla.server.schemas.v1.records import RecordUpdate
from argilla.server.schemas.v1.suggestions import Suggestion, SuggestionCreate
from argilla.server.search_engine import TextQuery

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from argilla.server.enums import DatasetStatus, FieldType, MetadataPropertyType
from argilla.server.models import QuestionSettings, QuestionType, ResponseStatus

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

QUESTION_CREATE_NAME_REGEX = r"^(?=.*[a-z0-9])[a-z0-9_-]+$"
QUESTION_CREATE_NAME_MIN_LENGTH = 1
QUESTION_CREATE_NAME_MAX_LENGTH = 200
QUESTION_CREATE_TITLE_MIN_LENGTH = 1
QUESTION_CREATE_TITLE_MAX_LENGTH = 500
QUESTION_CREATE_DESCRIPTION_MIN_LENGTH = 1
QUESTION_CREATE_DESCRIPTION_MAX_LENGTH = 1000

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

RATING_OPTIONS_MIN_ITEMS = 2
RATING_OPTIONS_MAX_ITEMS = 10

RATING_LOWER_VALUE_ALLOWED = 1
RATING_UPPER_VALUE_ALLOWED = 10

VALUE_TEXT_OPTION_VALUE_MIN_LENGTH = 1
VALUE_TEXT_OPTION_VALUE_MAX_LENGTH = 200
VALUE_TEXT_OPTION_TEXT_MIN_LENGTH = 1
VALUE_TEXT_OPTION_TEXT_MAX_LENGTH = 500
VALUE_TEXT_OPTION_DESCRIPTION_MIN_LENGTH = 1
VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH = 1000

LABEL_SELECTION_OPTIONS_MIN_ITEMS = 2
LABEL_SELECTION_OPTIONS_MAX_ITEMS = 250
LABEL_SELECTION_MIN_VISIBLE_OPTIONS = 3

RANKING_OPTIONS_MIN_ITEMS = 2
RANKING_OPTIONS_MAX_ITEMS = 50

TERMS_METADATA_PROPERTY_VALUES_MIN_ITEMS = 1
TERMS_METADATA_PROPERTY_VALUES_MAX_ITEMS = 250

RECORDS_CREATE_MIN_ITEMS = 1
RECORDS_CREATE_MAX_ITEMS = 1000

RECORDS_UPDATE_MIN_ITEMS = 1
RECORDS_UPDATE_MAX_ITEMS = 1000

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


class Metrics(BaseModel):
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


class TextQuestionSettingsCreate(BaseModel):
    type: Literal[QuestionType.text]
    use_markdown: bool = False


class UniqueValuesCheckerMixin(BaseModel):
    @root_validator
    def check_unique_values(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        options = values.get("options", [])
        seen = set()
        duplicates = set()
        for option in options:
            if option.value in seen:
                duplicates.add(option.value)
            else:
                seen.add(option.value)
        if duplicates:
            raise ValueError(f"Option values must be unique, found duplicates: {duplicates}")
        return values


class RatingQuestionSettingsOption(BaseModel):
    value: int


class RatingQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.rating]
    options: conlist(
        item_type=RatingQuestionSettingsOption,
        min_items=RATING_OPTIONS_MIN_ITEMS,
        max_items=RATING_OPTIONS_MAX_ITEMS,
    )

    @validator("options")
    def check_option_value_range(cls, options: List[RatingQuestionSettingsOption]):
        """Validator to control all values are in allowed range 1 <= x <= 10"""
        for option in options:
            if not RATING_LOWER_VALUE_ALLOWED <= option.value <= RATING_UPPER_VALUE_ALLOWED:
                raise ValueError(
                    f"Option value {option.value!r} out of range "
                    f"[{RATING_LOWER_VALUE_ALLOWED!r}, {RATING_UPPER_VALUE_ALLOWED!r}]"
                )
        return options


class ValueTextQuestionSettingsOption(BaseModel):
    value: constr(
        min_length=VALUE_TEXT_OPTION_VALUE_MIN_LENGTH,
        max_length=VALUE_TEXT_OPTION_VALUE_MAX_LENGTH,
    )
    text: constr(
        min_length=VALUE_TEXT_OPTION_TEXT_MIN_LENGTH,
        max_length=VALUE_TEXT_OPTION_TEXT_MAX_LENGTH,
    )
    description: Optional[
        constr(
            min_length=VALUE_TEXT_OPTION_DESCRIPTION_MIN_LENGTH,
            max_length=VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH,
        )
    ] = None


class LabelSelectionQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.label_selection]
    options: conlist(
        item_type=ValueTextQuestionSettingsOption,
        min_items=LABEL_SELECTION_OPTIONS_MIN_ITEMS,
        max_items=LABEL_SELECTION_OPTIONS_MAX_ITEMS,
    )
    visible_options: Optional[int] = PydanticField(None, ge=LABEL_SELECTION_MIN_VISIBLE_OPTIONS)

    @root_validator
    def check_visible_options_value(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        visible_options = values.get("visible_options")
        if visible_options is not None:
            num_options = len(values["options"])
            if visible_options > num_options:
                raise ValueError(
                    "The value for 'visible_options' must be less or equal to the number of items in 'options'"
                    f" ({num_options})"
                )
        return values


class MultiLabelSelectionQuestionSettingsCreate(LabelSelectionQuestionSettingsCreate):
    type: Literal[QuestionType.multi_label_selection]


class RankingQuestionSettingsCreate(UniqueValuesCheckerMixin):
    type: Literal[QuestionType.ranking]
    options: conlist(
        item_type=ValueTextQuestionSettingsOption,
        min_items=RANKING_OPTIONS_MIN_ITEMS,
        max_items=RANKING_OPTIONS_MAX_ITEMS,
    )


QuestionSettingsCreate = Annotated[
    Union[
        TextQuestionSettingsCreate,
        RatingQuestionSettingsCreate,
        LabelSelectionQuestionSettingsCreate,
        MultiLabelSelectionQuestionSettingsCreate,
        RankingQuestionSettingsCreate,
    ],
    PydanticField(discriminator="type"),
]


class Question(BaseModel):
    id: UUID
    name: str
    title: str
    description: Optional[str]
    required: bool
    settings: QuestionSettings
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Questions(BaseModel):
    items: List[Question]


QuestionName = Annotated[
    constr(
        regex=QUESTION_CREATE_NAME_REGEX,
        min_length=QUESTION_CREATE_NAME_MIN_LENGTH,
        max_length=QUESTION_CREATE_NAME_MAX_LENGTH,
    ),
    PydanticField(..., description="The name of the question"),
]

QuestionTitle = Annotated[
    constr(
        min_length=QUESTION_CREATE_TITLE_MIN_LENGTH,
        max_length=QUESTION_CREATE_TITLE_MAX_LENGTH,
    ),
    PydanticField(..., description="The title of the question"),
]

QuestionDescription = Annotated[
    constr(
        min_length=QUESTION_CREATE_DESCRIPTION_MIN_LENGTH,
        max_length=QUESTION_CREATE_DESCRIPTION_MAX_LENGTH,
    ),
    PydanticField(..., description="The description of the question"),
]


class QuestionCreate(BaseModel):
    name: QuestionName
    title: QuestionTitle
    description: Optional[QuestionDescription]
    required: Optional[bool]
    settings: QuestionSettingsCreate


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


class ResponseValue(BaseModel):
    value: Any


class ResponseValueCreate(BaseModel):
    value: Any


class Response(BaseModel):
    id: UUID
    values: Optional[Dict[str, ResponseValue]]
    status: ResponseStatus
    user_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


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
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        getter_dict = RecordGetterDict


class Records(BaseModel):
    items: List[Record]
    # TODO(@frascuchon): Make it required once fetch records without metadata filter computes also the total
    total: Optional[int] = None


class UserSubmittedResponseCreate(BaseModel):
    user_id: UUID
    values: Dict[str, ResponseValueCreate]
    status: Literal[ResponseStatus.submitted]


class UserDiscardedResponseCreate(BaseModel):
    user_id: UUID
    values: Optional[Dict[str, ResponseValueCreate]]
    status: Literal[ResponseStatus.discarded]


class UserDraftResponseCreate(BaseModel):
    user_id: UUID
    values: Dict[str, ResponseValueCreate]
    status: Literal[ResponseStatus.draft]


UserResponseCreate = Annotated[
    Union[UserSubmittedResponseCreate, UserDraftResponseCreate, UserDiscardedResponseCreate],
    PydanticField(discriminator="status"),
]


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


class RecordsCreate(BaseModel):
    items: conlist(item_type=RecordCreate, min_items=RECORDS_CREATE_MIN_ITEMS, max_items=RECORDS_CREATE_MAX_ITEMS)


class RecordUpdateWithId(RecordUpdate):
    id: UUID


class RecordsUpdate(BaseModel):
    # TODO: review this definition and align to create model
    items: List[RecordUpdateWithId] = PydanticField(
        ..., min_items=RECORDS_UPDATE_MIN_ITEMS, max_items=RECORDS_UPDATE_MAX_ITEMS
    )


class RecordIncludeParam(BaseModel):
    relationships: Optional[List[RecordInclude]] = PydanticField(None, alias="keys")
    vectors: Optional[List[str]] = PydanticField(None, alias="vectors")

    @root_validator
    def check(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        relationships = values.get("relationships")
        if not relationships:
            return values

        vectors = values.get("vectors")
        if vectors is not None and len(vectors) > 0 and RecordInclude.vectors in relationships:
            # TODO: once we have a exception handler for ValueError in v1, remove HTTPException
            # raise ValueError("Cannot include both 'vectors' and 'relationships' in the same request")
            raise HTTPException(
                status_code=422,
                detail="'include' query param cannot have both 'vectors' and 'vectors:vector_settings_name_1,vectors_settings_name_2,...'",
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


NT = TypeVar("NT", int, float)


class NumericMetadataProperty(GenericModel, Generic[NT]):
    min: Optional[NT] = None
    max: Optional[NT] = None

    @root_validator
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

    @root_validator
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


class RecordFilterScope(BaseModel):
    entity: Literal["record"]
    property: Union[Literal[RecordSortField.inserted_at], Literal[RecordSortField.updated_at]]


class ResponseFilterScope(BaseModel):
    entity: Literal["response"]
    question: Optional[QuestionName]
    property: Optional[Literal["status"]]


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

    @root_validator
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
