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
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from rubrix.client.sdk.commons.models import (
    BaseAnnotation,
    BaseRecord,
    PredictionStatus,
    ScoreRange,
    TaskStatus,
    UpdateDatasetRequest,
)


class Text2TextPrediction(BaseModel):
    text: str
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class Text2TextAnnotation(BaseAnnotation):
    sentences: List[Text2TextPrediction]


class CreationText2TextRecord(BaseRecord[Text2TextAnnotation]):
    text: str


class Text2TextRecord(CreationText2TextRecord):
    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")


class Text2TextBulkData(UpdateDatasetRequest):
    records: List[CreationText2TextRecord]


class Text2TextQuery(BaseModel):
    ids: Optional[List[Union[str, int]]]

    query_text: str = Field(default=None)

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    score: Optional[ScoreRange] = Field(default=None)

    status: List[TaskStatus] = Field(default_factory=list)

    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None
