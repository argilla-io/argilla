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

from pydantic import BaseModel, Field, StrictInt, StrictStr, conint


class FeedbackDatasetModel(BaseModel):
    id: UUID
    name: str = Field(regex="^(?!-|_)[a-zA-Z0-9-_ ]+$")
    guidelines: Optional[str] = None
    status: Optional[str] = None
    workspace_id: Optional[UUID] = None
    inserted_at: datetime
    updated_at: datetime


class FeedbackRankingValueModel(BaseModel):
    value: StrictStr
    rank: Optional[conint(ge=1)] = None


class FeedbackValueModel(BaseModel):
    value: Union[StrictStr, StrictInt, List[str], List[FeedbackRankingValueModel]]


class FeedbackResponseStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"


class FeedbackResponseStatusFilter(str, Enum):
    draft = "draft"
    missing = "missing"  # not a status as-is, used as a filter to indicate no response
    submitted = "submitted"
    discarded = "discarded"


class FeedbackResponseModel(BaseModel):
    id: UUID
    values: Dict[str, FeedbackValueModel]
    status: FeedbackResponseStatus
    user_id: UUID
    inserted_at: datetime
    updated_at: datetime


class FeedbackSuggestionModel(BaseModel):
    id: UUID
    question_id: UUID
    type: Optional[Literal["human", "model"]] = None
    score: Optional[float] = None
    value: Any
    agent: Optional[str] = None


class FeedbackItemModel(BaseModel):
    id: UUID
    fields: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None
    responses: Optional[List[FeedbackResponseModel]] = []
    suggestions: Optional[List[FeedbackSuggestionModel]] = []
    inserted_at: datetime
    updated_at: datetime


class FeedbackRecordsModel(BaseModel):
    items: List[FeedbackItemModel]


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


class FeedbackRecordsMetricsModel(BaseModel):
    count: int


class FeedbackMetricsModel(BaseModel):
    records: FeedbackRecordsMetricsModel
