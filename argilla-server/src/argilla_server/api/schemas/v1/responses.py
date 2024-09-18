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

from fastapi import Body

from argilla_server.api.schemas.v1.questions import QuestionName
from argilla_server.enums import ResponseStatus

# from argilla_server.pydantic_v1 import BaseModel, Field, StrictInt, StrictStr, root_validator
from pydantic import model_validator, BaseModel, Field, ConfigDict, StrictInt, StrictStr

RESPONSES_BULK_CREATE_MIN_ITEMS = 1
RESPONSES_BULK_CREATE_MAX_ITEMS = 100

SPAN_QUESTION_RESPONSE_VALUE_MAX_ITEMS = 10_000

SPAN_QUESTION_RESPONSE_VALUE_ITEM_START_GREATER_THAN_OR_EQUAL = 0
SPAN_QUESTION_RESPONSE_VALUE_ITEM_END_GREATER_THAN_OR_EQUAL = 1


class RankingQuestionResponseValueItem(BaseModel):
    value: str
    rank: Optional[int]


class SpanQuestionResponseValueItem(BaseModel):
    label: str
    start: int = Field(..., ge=SPAN_QUESTION_RESPONSE_VALUE_ITEM_START_GREATER_THAN_OR_EQUAL)
    end: int = Field(..., ge=SPAN_QUESTION_RESPONSE_VALUE_ITEM_END_GREATER_THAN_OR_EQUAL)

    @model_validator(mode="before")
    @classmethod
    def check_start_and_end(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        start, end = values.get("start"), values.get("end")

        if start is not None and end is not None and end <= start:
            raise ValueError("span question response value 'end' must have a value greater than 'start'")

        return values


RankingQuestionResponseValue = List[RankingQuestionResponseValueItem]
SpanQuestionResponseValue = Annotated[
    List[SpanQuestionResponseValueItem], Field(..., max_items=SPAN_QUESTION_RESPONSE_VALUE_MAX_ITEMS)
]
MultiLabelSelectionQuestionResponseValue = List[str]
RatingQuestionResponseValue = StrictInt
TextAndLabelSelectionQuestionResponseValue = StrictStr

ResponseValueTypes = Union[
    SpanQuestionResponseValue,
    RankingQuestionResponseValue,
    MultiLabelSelectionQuestionResponseValue,
    RatingQuestionResponseValue,
    TextAndLabelSelectionQuestionResponseValue,
]


class ResponseValue(BaseModel):
    value: Any


class ResponseValueCreate(BaseModel):
    value: ResponseValueTypes


class ResponseValueUpdate(BaseModel):
    value: ResponseValueTypes


ResponseValues = Dict[str, ResponseValue]
ResponseValuesCreate = Dict[QuestionName, ResponseValueCreate]
ResponseValuesUpdate = Dict[QuestionName, ResponseValueUpdate]


class Response(BaseModel):
    id: UUID
    values: Optional[ResponseValues]
    status: ResponseStatus
    record_id: UUID
    user_id: UUID
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseCreate(BaseModel):
    values: Optional[ResponseValuesCreate]
    status: ResponseStatus


class ResponseFilterScope(BaseModel):
    entity: Literal["response"]
    question: Optional[QuestionName]
    property: Optional[Literal["status"]]


class SubmittedResponseUpdate(BaseModel):
    values: ResponseValuesUpdate
    status: Literal[ResponseStatus.submitted]


class DiscardedResponseUpdate(BaseModel):
    values: Optional[ResponseValuesUpdate]
    status: Literal[ResponseStatus.discarded]


class DraftResponseUpdate(BaseModel):
    values: Optional[ResponseValuesUpdate]
    status: Literal[ResponseStatus.draft]


ResponseUpdate = Annotated[
    Union[SubmittedResponseUpdate, DiscardedResponseUpdate, DraftResponseUpdate],
    Body(..., discriminator="status"),
]


class SubmittedResponseUpsert(BaseModel):
    values: ResponseValuesUpdate
    status: Literal[ResponseStatus.submitted]
    record_id: UUID


class DiscardedResponseUpsert(BaseModel):
    values: Optional[ResponseValuesUpdate]
    status: Literal[ResponseStatus.discarded]
    record_id: UUID


class DraftResponseUpsert(BaseModel):
    values: Optional[ResponseValuesUpdate]
    status: Literal[ResponseStatus.draft]
    record_id: UUID


ResponseUpsert = Annotated[
    Union[SubmittedResponseUpsert, DiscardedResponseUpsert, DraftResponseUpsert],
    Body(..., discriminator="status"),
]


class ResponsesBulkCreate(BaseModel):
    items: List[ResponseUpsert] = Field(
        ...,
        min_items=RESPONSES_BULK_CREATE_MIN_ITEMS,
        max_items=RESPONSES_BULK_CREATE_MAX_ITEMS,
    )


class ResponseBulkError(BaseModel):
    detail: str


class ResponseBulk(BaseModel):
    item: Optional[Response]
    error: Optional[ResponseBulkError]


class ResponsesBulk(BaseModel):
    items: List[ResponseBulk]


class UserDraftResponseCreate(BaseModel):
    user_id: UUID
    values: ResponseValuesCreate
    status: Literal[ResponseStatus.draft]


class UserDiscardedResponseCreate(BaseModel):
    user_id: UUID
    values: Optional[ResponseValuesCreate]
    status: Literal[ResponseStatus.discarded]


class UserSubmittedResponseCreate(BaseModel):
    user_id: UUID
    values: ResponseValuesCreate
    status: Literal[ResponseStatus.submitted]


UserResponseCreate = Annotated[
    Union[UserSubmittedResponseCreate, UserDraftResponseCreate, UserDiscardedResponseCreate],
    Field(discriminator="status"),
]
