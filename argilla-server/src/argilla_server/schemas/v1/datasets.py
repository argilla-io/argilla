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
from typing import List, Optional
from uuid import UUID

from argilla_server.enums import DatasetStatus
from argilla_server.pydantic_v1 import BaseModel, Field, constr
from argilla_server.schemas.base import UpdateSchema

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

DATASET_NAME_REGEX = r"^(?!-|_)[a-zA-Z0-9-_ ]+$"
DATASET_NAME_MIN_LENGTH = 1
DATASET_NAME_MAX_LENGTH = 200
DATASET_GUIDELINES_MIN_LENGTH = 1
DATASET_GUIDELINES_MAX_LENGTH = 10000


DatasetName = Annotated[
    constr(regex=DATASET_NAME_REGEX, min_length=DATASET_NAME_MIN_LENGTH, max_length=DATASET_NAME_MAX_LENGTH),
    Field(..., description="Dataset name"),
]


DatasetGuidelines = Annotated[
    constr(min_length=DATASET_GUIDELINES_MIN_LENGTH, max_length=DATASET_GUIDELINES_MAX_LENGTH),
    Field(..., description="Dataset guidelines"),
]


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


class DatasetProgress(BaseModel):
    total: int
    submitted: int
    discarded: int
    conflicting: int
    pending: int


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
