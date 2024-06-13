#  coding=utf-8
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
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from argilla_v1.pydantic_v1 import BaseModel, Field, StrictStr, conint, root_validator


class FeedbackDatasetModel(BaseModel):
    id: UUID
    name: str = Field(regex="^(?!-|_)[a-zA-Z0-9-_ ]+$")
    guidelines: Optional[str] = None
    # Set default for backward compatibility
    allow_extra_metadata: Optional[bool] = True
    status: Optional[str] = None
    workspace_id: Optional[UUID] = None
    last_activity_at: Optional[datetime] = None
    inserted_at: datetime
    updated_at: datetime


class FeedbackRankingValueModel(BaseModel):
    value: StrictStr
    rank: Optional[conint(ge=1)] = None


class FeedbackValueModel(BaseModel):
    value: Any


class FeedbackResponseStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"


# TODO: these models shouldn't transform the payload from the server to not JSON serializable types (UUID, datetime, etc)


class FeedbackResponseModel(BaseModel):
    id: UUID
    values: Union[Dict[str, FeedbackValueModel], None]
    status: FeedbackResponseStatus
    user_id: Optional[UUID]  # Support changes introduced in https://github.com/argilla-io/argilla-server/pull/57
    inserted_at: datetime
    updated_at: datetime


class FeedbackSuggestionModel(BaseModel):
    id: UUID
    question_id: str
    type: Optional[Literal["human", "model"]] = None
    score: Optional[Union[float, List[float]]] = None
    value: Any
    agent: Optional[str] = None


class FeedbackItemModel(BaseModel):
    id: UUID
    fields: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None
    responses: Optional[List[FeedbackResponseModel]] = []
    vectors: Optional[Dict[str, List[float]]] = None
    suggestions: Optional[List[FeedbackSuggestionModel]] = []
    vectors: Optional[Dict[str, List[float]]] = {}
    inserted_at: datetime
    updated_at: datetime


class FeedbackRecordsModel(BaseModel):
    items: List[FeedbackItemModel]
    total: int


# TODO: `query_score` naming can be improved to simply `score`. (frontend should be aligned)
# TODO: Maybe `query_score` should not be optional.
class FeedbackRecordSearchModel(BaseModel):
    record: FeedbackItemModel
    query_score: Optional[float]


class FeedbackRecordsSearchModel(BaseModel):
    items: List[FeedbackRecordSearchModel]
    total: int


class FeedbackRecordsSearchVectorQuery(BaseModel):
    name: str
    record_id: Optional[UUID] = None
    value: Optional[List[float]] = None

    @root_validator(skip_on_failure=True)
    def check_required(cls, values: dict) -> dict:
        """Check that either 'record_id' or 'value' is provided"""
        record_id = values.get("record_id")
        value = values.get("value")

        if bool(record_id) == bool(value):
            raise ValueError("Either 'record_id' or 'value' must be provided")

        return values


class FeedbackFieldModel(BaseModel):
    id: UUID
    name: str
    title: str
    required: bool
    settings: Dict[str, Any]
    inserted_at: datetime
    updated_at: datetime


class FeedbackQuestionModel(BaseModel):
    id: UUID
    name: str
    title: str
    description: Optional[str] = None
    required: bool
    settings: Dict[str, Any]
    inserted_at: datetime
    updated_at: datetime


class FeedbackMetadataPropertyModel(BaseModel):
    id: UUID
    name: str
    title: str
    visible_for_annotators: bool
    settings: Dict[str, Any]
    inserted_at: datetime
    updated_at: datetime


class FeedbackRecordsMetricsModel(BaseModel):
    count: int


class FeedbackVectorSettingsModel(BaseModel):
    id: UUID
    name: str
    title: str
    dimensions: int
    inserted_at: datetime
    updated_at: datetime


class FeedbackListVectorSettingsModel(BaseModel):
    items: List[FeedbackVectorSettingsModel]


class FeedbackMetricsModel(BaseModel):
    records: FeedbackRecordsMetricsModel
