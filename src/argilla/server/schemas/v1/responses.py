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
from typing_extensions import Annotated

from argilla.server.models import ResponseStatus
from argilla.server.pydantic_v1 import BaseModel, Field
from argilla.server.schemas.v1.questions import QuestionName

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

RESPONSES_BULK_CREATE_MIN_ITEMS = 1
RESPONSES_BULK_CREATE_MAX_ITEMS = 100


class ResponseValue(BaseModel):
    value: Any


class ResponseValueCreate(BaseModel):
    value: Any


class ResponseValueUpdate(BaseModel):
    value: Any


class Response(BaseModel):
    id: UUID
    values: Optional[Dict[str, ResponseValue]]
    status: ResponseStatus
    record_id: UUID
    user_id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ResponseCreate(BaseModel):
    values: Optional[Dict[str, ResponseValueCreate]]
    status: ResponseStatus


class ResponseFilterScope(BaseModel):
    entity: Literal["response"]
    question: Optional[QuestionName]
    property: Optional[Literal["status"]]


class SubmittedResponseUpdate(BaseModel):
    values: Dict[str, ResponseValueUpdate]
    status: Literal[ResponseStatus.submitted]


class DiscardedResponseUpdate(BaseModel):
    values: Optional[Dict[str, ResponseValueUpdate]]
    status: Literal[ResponseStatus.discarded]


class DraftResponseUpdate(BaseModel):
    values: Optional[Dict[str, ResponseValueUpdate]]
    status: Literal[ResponseStatus.draft]


ResponseUpdate = Annotated[
    Union[SubmittedResponseUpdate, DiscardedResponseUpdate, DraftResponseUpdate],
    Body(..., discriminator="status"),
]


class SubmittedResponseUpsert(BaseModel):
    values: Dict[str, ResponseValueUpdate]
    status: Literal[ResponseStatus.submitted]
    record_id: UUID


class DiscardedResponseUpsert(BaseModel):
    values: Optional[Dict[str, ResponseValueUpdate]]
    status: Literal[ResponseStatus.discarded]
    record_id: UUID


class DraftResponseUpsert(BaseModel):
    values: Optional[Dict[str, ResponseValueUpdate]]
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
    values: Dict[str, ResponseValueCreate]
    status: Literal[ResponseStatus.draft]


class UserDiscardedResponseCreate(BaseModel):
    user_id: UUID
    values: Optional[Dict[str, ResponseValueCreate]]
    status: Literal[ResponseStatus.discarded]


class UserSubmittedResponseCreate(BaseModel):
    user_id: UUID
    values: Dict[str, ResponseValueCreate]
    status: Literal[ResponseStatus.submitted]


UserResponseCreate = Annotated[
    Union[UserSubmittedResponseCreate, UserDraftResponseCreate, UserDiscardedResponseCreate],
    Field(discriminator="status"),
]
