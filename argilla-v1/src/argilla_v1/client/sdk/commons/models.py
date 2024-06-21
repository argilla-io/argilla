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
import socket
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Generic, List, MutableMapping, Optional, TypeVar, Union
from uuid import uuid4

from argilla_v1.client.models import Vectors as ClientVectors
from argilla_v1.pydantic_v1 import BaseModel, Field, validator
from argilla_v1.pydantic_v1.generics import GenericModel

if TYPE_CHECKING:
    from httpx import Response as HTTPXResponse

MACHINE_NAME = socket.gethostname()


class TaskStatus(str, Enum):
    default = "Default"
    edited = "Edited"
    discarded = "Discarded"
    validated = "Validated"


class BaseAnnotation(BaseModel):
    agent: str = Field(max_length=64)


T = TypeVar("T", bound=BaseAnnotation)


class VectorInfo(BaseModel):
    """Record vector info for api layer data model"""

    value: List[float]


SdkVectors = Dict[str, VectorInfo]


class SdkVectorSearch(BaseModel):
    """The sdk vector search parameters"""

    name: str
    value: List[float]


class BaseRecord(GenericModel, Generic[T]):
    id: Optional[Union[int, str]] = Field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = Field(default=None)
    event_timestamp: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    prediction: Optional[T] = None
    annotation: Optional[T] = None
    vectors: Optional[SdkVectors] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    search_keywords: Optional[List[str]] = None

    # this is a small hack to get a json-compatible serialization on cls.dict(), which we use for the httpx calls.
    # they want to build this feature into pydantic, see https://github.com/samuelcolvin/pydantic/issues/1409
    @validator("event_timestamp")
    def datetime_to_isoformat(cls, v: Optional[datetime]):
        if v is not None:
            return v.isoformat()

    @staticmethod
    def _from_client_vectors(vectors: ClientVectors) -> SdkVectors:
        sdk_vectors = None
        if vectors:
            sdk_vectors = {name: VectorInfo(value=vector) for name, vector in vectors.items()}
        return sdk_vectors

    @staticmethod
    def _to_client_vectors(vectors: SdkVectors) -> ClientVectors:
        client_vectors = None
        if vectors:
            client_vectors = {name: vector.value for name, vector in vectors.items()}
        return client_vectors


class UpdateDatasetRequest(BaseModel):
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PredictionStatus(str, Enum):
    OK = "ok"
    KO = "ko"


class ScoreRange(BaseModel):
    range_from: float = Field(default=0.0, alias="from")
    range_to: float = Field(default=None, alias="to")


R = TypeVar("R")


class Response(GenericModel, Generic[R]):
    status_code: int
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[R]

    @classmethod
    def from_httpx_response(cls, response: "HTTPXResponse") -> "Response[R]":
        return cls(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
        )


class BulkResponse(BaseModel):
    dataset: str
    processed: int
    failed: int = 0


class ErrorMessage(BaseModel):
    detail: str


class ValidationError(BaseModel):
    loc: List[str]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: List[ValidationError]
