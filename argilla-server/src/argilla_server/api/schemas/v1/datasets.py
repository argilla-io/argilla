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
from typing import List, Literal, Optional, Union
from uuid import UUID

from argilla_server.api.schemas.v1.commons import UpdateSchema
from argilla_server.enums import DatasetDistributionStrategy, DatasetStatus
from argilla_server.pydantic_v1 import BaseModel, Field, constr

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

DATASET_NAME_MIN_LENGTH = 1
DATASET_NAME_MAX_LENGTH = 200
DATASET_GUIDELINES_MIN_LENGTH = 1
DATASET_GUIDELINES_MAX_LENGTH = 10000

DatasetName = Annotated[
    constr(
        min_length=DATASET_NAME_MIN_LENGTH,
        max_length=DATASET_NAME_MAX_LENGTH,
    ),
    Field(..., description="Dataset name"),
]

DatasetGuidelines = Annotated[
    constr(min_length=DATASET_GUIDELINES_MIN_LENGTH, max_length=DATASET_GUIDELINES_MAX_LENGTH),
    Field(..., description="Dataset guidelines"),
]


class DatasetOverlapDistribution(BaseModel):
    strategy: Literal[DatasetDistributionStrategy.overlap]
    min_submitted: int


DatasetDistribution = DatasetOverlapDistribution


class DatasetOverlapDistributionCreate(BaseModel):
    strategy: Literal[DatasetDistributionStrategy.overlap]
    min_submitted: int = Field(
        ge=1,
        description="Minimum number of submitted responses to consider a record as completed",
    )


DatasetDistributionCreate = DatasetOverlapDistributionCreate


class DatasetOverlapDistributionUpdate(DatasetDistributionCreate):
    pass


DatasetDistributionUpdate = DatasetOverlapDistributionUpdate


class ResponseMetrics(BaseModel):
    total: int
    submitted: int
    discarded: int
    draft: int
    pending: int


class DatasetMetrics(BaseModel):
    responses: ResponseMetrics


class DatasetProgress(BaseModel):
    total: int
    completed: int
    pending: int


class RecordResponseDistribution(BaseModel):
    submitted: int = 0
    discarded: int = 0
    draft: int = 0


class UserProgress(BaseModel):
    username: str
    completed: RecordResponseDistribution = RecordResponseDistribution()
    pending: RecordResponseDistribution = RecordResponseDistribution()


class UsersProgress(BaseModel):
    users: List[UserProgress]


class Dataset(BaseModel):
    id: UUID
    name: str
    guidelines: Optional[str]
    allow_extra_metadata: bool
    status: DatasetStatus
    distribution: DatasetDistribution
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
    distribution: DatasetDistributionCreate = DatasetOverlapDistributionCreate(
        strategy=DatasetDistributionStrategy.overlap,
        min_submitted=1,
    )
    workspace_id: UUID


class DatasetUpdate(UpdateSchema):
    name: Optional[DatasetName]
    guidelines: Optional[DatasetGuidelines]
    allow_extra_metadata: Optional[bool]
    distribution: Optional[DatasetDistributionUpdate]

    __non_nullable_fields__ = {"name", "allow_extra_metadata", "distribution"}
