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
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class UserEventSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str] = None
    username: str
    role: str
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceEventSchema(BaseModel):
    id: UUID
    name: str
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetQuestionEventSchema(BaseModel):
    id: UUID
    name: str
    title: str
    description: Optional[str] = None
    required: bool
    settings: dict
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetFieldEventSchema(BaseModel):
    id: UUID
    name: str
    title: str
    required: bool
    settings: dict
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetMetadataPropertyEventSchema(BaseModel):
    id: UUID
    name: str
    title: str
    settings: dict
    visible_for_annotators: bool
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetVectorSettingsEventSchema(BaseModel):
    id: UUID
    name: str
    title: str
    dimensions: int
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetEventSchema(BaseModel):
    id: UUID
    name: str
    guidelines: Optional[str] = None
    allow_extra_metadata: bool
    status: str
    distribution: dict
    workspace: WorkspaceEventSchema
    questions: List[DatasetQuestionEventSchema]
    fields: List[DatasetFieldEventSchema]
    metadata_properties: List[DatasetMetadataPropertyEventSchema]
    vectors_settings: List[DatasetVectorSettingsEventSchema]
    last_activity_at: datetime
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecordEventSchema(BaseModel):
    id: UUID
    status: str
    # TODO: Truncate fields so we don't respond with big field values.
    # Or find another possible solution.
    fields: dict
    metadata: Optional[dict] = Field(None, alias="metadata_")
    external_id: Optional[str] = None
    # TODO:
    # responses:
    # - Create a new `GET /api/v1/records/{record_id}/responses` endpoint.
    # - Or use `/api/v1/records/{record_id}` endpoint.
    # - Other possible alternative is to expand the responses here but using
    #   a RecordResponseEventSchema not including the record inside.
    # suggestions:
    # - Can use `GET /api/v1/records/{record_id}/suggestions` endpoint.
    # - Or use `/api/v1/records/{record_id}` endpoint.
    # - Other possible alternative is to expand the suggestions here but using
    #   a RecordSuggestionEventSchema not including the record inside.
    # vectors:
    # - Create a new `GET /api/v1/records/{record_id}/vectors` endpoint.
    # - Or use `/api/v1/records/{record_id}` endpoint.
    # - Other possible alternative is to expand the vectors here but using
    #   a RecordVectorEventSchema not including the record inside.
    dataset: DatasetEventSchema
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseEventSchema(BaseModel):
    id: UUID
    values: Optional[dict] = None
    status: str
    record: RecordEventSchema
    user: UserEventSchema
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
