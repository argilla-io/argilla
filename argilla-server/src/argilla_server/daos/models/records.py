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

import uuid
import warnings
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from argilla_server import _messages
from argilla_server.commons.models import PredictionStatus, TaskStatus, TaskType
from argilla_server.constants import JS_MAX_SAFE_INTEGER, PROTECTED_METADATA_FIELD_PREFIX
from argilla_server.daos.backend.search.model import BaseRecordsQuery, SortConfig
from argilla_server.helpers import flatten_dict
from argilla_server.pydantic_v1 import BaseModel, Field, conint, constr, root_validator, validator
from argilla_server.pydantic_v1.generics import GenericModel
from argilla_server.settings import settings
from argilla_server.utils import limit_value_length


class DaoRecordsSearch(BaseModel):
    query: Optional[BaseRecordsQuery] = None
    sort: SortConfig = Field(default_factory=SortConfig)


class DaoRecordsSearchResults(BaseModel):
    total: int
    records: List[Dict[str, Any]]


class BaseAnnotationDB(BaseModel):
    agent: Optional[str] = Field(
        None,
        max_length=64,
    )


class BaseEmbeddingVectorDB(BaseModel):
    value: List[float]
    record_properties: Optional[List[Union[str, Dict[str, Any]]]]
    model: Optional[str]


AnnotationDB = TypeVar("AnnotationDB", bound=BaseAnnotationDB)
EmbeddingDB = TypeVar("EmbeddingDB", bound=BaseEmbeddingVectorDB)


class BaseRecordInDB(GenericModel, Generic[AnnotationDB]):
    id: Optional[Union[conint(strict=True), constr(strict=True)]] = None
    metadata: Dict[str, Any] = Field(default=None)
    event_timestamp: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    prediction: Optional[AnnotationDB] = Field(None, description="Deprecated. Use `predictions` instead")
    annotation: Optional[AnnotationDB] = None

    vectors: Optional[Dict[str, BaseEmbeddingVectorDB]] = Field(
        None,
        description="Provide the vector info as a list of key - value dictionary. "
        "The dictionary contains the dimension and dimension sized vector float list",
    )

    predictions: Optional[Dict[str, AnnotationDB]] = Field(
        None,
        description="Provide the prediction info as a key-value dictionary. "
        "The key will represent the agent ant the value the prediction. "
        "Using this way you can skip passing the agent inside of the prediction",
    )
    annotations: Optional[Dict[str, AnnotationDB]] = Field(
        None,
        description="Provide the annotation info as a key-value dictionary. "
        "The key will represent the agent ant the value the annotation. "
        "Using this way you can skip passing the agent inside the annotation",
    )

    @staticmethod
    def update_annotation(values, annotation_field: str):
        field_to_update = f"{annotation_field}s"
        annotation = values.get(annotation_field)
        annotations = values.get(field_to_update) or {}

        if annotations:
            for key, value in annotations.items():
                value.agent = None  # Maybe we want key and agents with different values

        if annotation:
            if not annotation.agent:
                raise AssertionError("Agent must be defined!")

            annotations.update({annotation.agent: annotation.__class__.parse_obj(annotation.dict(exclude={"agent"}))})
            values[field_to_update] = annotations

        if annotations and not annotation:
            # set first annotation
            key, value = list(annotations.items())[0]
            values[annotation_field] = value.__class__(agent=key, **value.dict(exclude={"agent"}))

        return values

    @root_validator(skip_on_failure=True)
    def prepare_record_for_db(cls, values):
        values = cls.update_annotation(values, "prediction")
        values = cls.update_annotation(values, "annotation")

        return values

    @validator("id", always=True, pre=True)
    def _normalize_id(cls, v):
        if v is None:
            return str(uuid.uuid4())
        if isinstance(v, int):
            message = (
                f"Integer ids won't be supported in future versions. We recommend to start using strings instead. "
                "For datasets already containing integer values we recommend migrating them to avoid deprecation issues. "
                "See https://docs.argilla.io/en/latest/getting_started/installation/configurations"
                "/database_migrations.html#elasticsearch"
            )
            warnings.warn(message, DeprecationWarning)
            # See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER
            if v > JS_MAX_SAFE_INTEGER:
                message = (
                    "You've provided a big integer value. Use a string instead, otherwise you may experience some "
                    "problems using the UI. See "
                    "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number"
                    "/MAX_SAFE_INTEGER"
                )
                warnings.warn(message, UserWarning)
        return v

    @validator("status", always=True)
    def fill_default_value(cls, status: TaskStatus):
        """Fastapi validator for set default task status"""
        return TaskStatus.default if status is None else status

    @validator("metadata", pre=True)
    def parse_metadata(cls, metadata: Dict[str, Any]):
        """
        A FastAPI validator for parsing metadata dictionary

        Parameters
        ----------
        metadata:
            The metadata dictionary

        Returns
        -------
            A flatten version of metadata dictionary

        """
        if metadata:
            metadata_protected = {}
            metadata_parsed = {}

            for k, v in metadata.items():
                if k.startswith(PROTECTED_METADATA_FIELD_PREFIX):
                    metadata_protected[k] = v
                else:
                    metadata_parsed[k] = limit_value_length(v, settings.metadata_field_length)

            metadata_parsed = {**flatten_dict(metadata_parsed, drop_empty=True), **metadata_protected}

            if metadata != metadata_parsed:
                message = (
                    "Some metadata values exceed the max length. Those values will be"
                    f" truncated by keeping only the last {settings.metadata_field_length} characters. "
                    + _messages.ARGILLA_METADATA_FIELD_WARNING_MESSAGE
                )
                warnings.warn(message, UserWarning)
                metadata = metadata_parsed
        return metadata

    @classmethod
    def task(cls) -> TaskType:
        """The task type related to this task info"""
        raise NotImplementedError

    @property
    def predicted(self) -> Optional[PredictionStatus]:
        """The task record prediction status (if any)"""
        return None

    @property
    def predicted_as(self) -> Optional[List[str]]:
        """Predictions strings representation"""
        return None

    @property
    def annotated_as(self) -> Optional[List[str]]:
        """Annotations strings representation"""
        return None

    @property
    def scores(self) -> Optional[List[float]]:
        """Prediction scores"""
        return None

    def all_text(self) -> str:
        """All textual information related to record"""
        raise NotImplementedError

    @property
    def predicted_by(self) -> List[str]:
        """The prediction agents"""
        if self.prediction:
            return [self.prediction.agent]
        return []

    @property
    def annotated_by(self) -> List[str]:
        """The annotation agents"""
        if self.annotation:
            return [self.annotation.agent]
        return []

    def extended_fields(self) -> Dict[str, Any]:
        """
        Used for extends fields to store in db. Tasks that would include extra
        properties than commons (predicted, annotated_as,....) could implement
        this method.
        """
        return {
            "predicted": self.predicted,
            "annotated_as": self.annotated_as,
            "predicted_as": self.predicted_as,
            "annotated_by": self.annotated_by,
            "predicted_by": self.predicted_by,
            "score": self.scores,
        }

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Extends base component dict extending object properties
        and user defined extended fields
        """
        return {
            **super().dict(*args, **kwargs),
            **self.extended_fields(),
        }


class BaseRecordDB(BaseRecordInDB, Generic[AnnotationDB]):
    # Read only ones
    metrics: Dict[str, Any] = Field(default_factory=dict)
    search_keywords: Optional[List[str]] = None
    last_updated: datetime = None

    @validator("search_keywords")
    def remove_duplicated_keywords(cls, value) -> List[str]:
        """Remove duplicated keywords"""
        if value:
            return list(set(value))


RecordDB = TypeVar("RecordDB", bound=BaseRecordDB)
