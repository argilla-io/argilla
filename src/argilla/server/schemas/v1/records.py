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
import json
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, conlist, constr


class AnnotationAnswer(BaseModel):
    value: Any


class PredictionAnswer(BaseModel):
    value: Any
    score: float = 0.0


Annotation = Dict[str, AnnotationAnswer]
Prediction = Dict[str, PredictionAnswer]


class ResponseItem(BaseModel):
    value: Any


Response = Dict[constr(regex=r"^[a-z\d_-]+$"), ResponseItem]


class Record(BaseModel):
    id: UUID

    fields: Dict[str, Any]
    responses: Optional[Dict[str, Response]]

    metadata: Optional[Dict[str, Any]]
    vectors: Optional[Dict[str, List[float]]]

    class Config:
        orm_mode = True


class RecordCreate(BaseModel):
    fields: Dict[str, Any]
    external_id: Optional[str]
    response: Optional[Response]


class RecordsCreate(BaseModel):
    items: conlist(item_type=RecordCreate, min_items=1, max_items=1000)


class RecordInclude(str, Enum):
    responses = "responses"
    suggestions = "suggestions"
    vectors = "vectors"
    metadata = "metadata"


class RecordsList(BaseModel):
    total: int
    items: List[Record]
