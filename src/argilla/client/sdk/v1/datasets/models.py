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

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from pydantic import BaseModel, Field, StrictInt, StrictStr


class FeedbackDatasetModel(BaseModel):
    id: UUID
    name: str = Field(regex="^(?!-|_)[a-zA-Z0-9-_ ]+$")
    guidelines: str = None
    status: str = None
    workspace_id: str = None
    created_at: datetime = None
    last_updated: datetime = None


class FeedbackValueModel(BaseModel):
    value: Union[StrictStr, StrictInt]


class FeedbackResponseModel(BaseModel):
    id: UUID
    values: Dict[str, FeedbackValueModel]
    status: Literal["submitted", "missing", "discarded"]
    user_id: UUID
    inserted_at: datetime
    updated_at: datetime


class FeedbackItemModel(BaseModel):
    id: UUID
    fields: Dict[str, Any]
    external_id: Optional[str] = None
    responses: List[FeedbackResponseModel] = []
    inserted_at: datetime
    updated_at: datetime


class FeedbackRecordsModel(BaseModel):
    items: List[FeedbackItemModel]
    total: Optional[int] = None

    class Config:
        fields = {"total": {"exclude": True}}


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
    description: str
    required: bool
    settings: Dict[str, Any]
    inserted_at: datetime
    updated_at: datetime
