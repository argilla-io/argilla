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
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from argilla.server.models import ResponseStatus
from argilla.server.schemas.base import UpdateSchema
from argilla.server.schemas.v1.suggestions import SuggestionCreate


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


class ResponseCreate(BaseModel):
    values: Optional[Dict[str, ResponseValueCreate]]
    status: ResponseStatus


class RecordUpdate(UpdateSchema):
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    suggestions: Optional[List[SuggestionCreate]] = None
    vectors: Optional[Dict[str, List[float]]]
