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

from uuid import UUID
from typing import Optional
from datetime import datetime

from argilla_server.pydantic_v1 import BaseModel, Field


class UserEventSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str]
    username: str
    role: str
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WorkspaceEventSchema(BaseModel):
    id: UUID
    name: str
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DatasetEventSchema(BaseModel):
    id: UUID
    name: str
    guidelines: Optional[str]
    allow_extra_metadata: bool
    status: str
    distribution: dict
    workspace: WorkspaceEventSchema
    last_activity_at: datetime
    inserted_at: datetime
    updated_at: datetime

    # TODO: Additional expanded resources that can be added to DatasetSchema:
    # * questions
    # * fields
    # * metadata_properties
    # * vector_settings

    class Config:
        orm_mode = True


class RecordEventSchema(BaseModel):
    id: UUID
    status: str
    fields: dict
    metadata: Optional[dict] = Field(None, alias="metadata_")
    external_id: Optional[str]
    # responses: Can be retrieved using the responses endpoint.
    # suggestions: Can be retrieved using the suggestions endpoint.
    # vectors: We don't have and endpoint for these.
    dataset: DatasetEventSchema
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ResponseEventSchema(BaseModel):
    id: UUID
    values: Optional[dict]
    status: str
    record: RecordEventSchema
    user: UserEventSchema
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
