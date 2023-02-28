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
import warnings
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.generics import GenericModel

from argilla import _messages
from argilla.server.commons.models import PredictionStatus, TaskStatus, TaskType
from argilla.server.daos.backend.search.model import BaseRecordsQuery, SortConfig
from argilla.server.helpers import flatten_dict
from argilla.server.settings import settings
from argilla.utils import limit_value_length


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
    id: Optional[Union[int, str]] = Field(default=None)
    metadata: Dict[str, Any] = Field(default=None)
    event_timestamp: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    prediction: Optional[AnnotationDB] = Field(None, description="Deprecated. Use `predictions` instead")
    annotation: Optional[AnnotationDB] = None

    vectors: Optional[Dict[str, BaseEmbeddingVectorDB]] = Field(
        None,
        description="Provide the vector info as a list of key - value dictionary."
        "The dictionary contains the dimension and dimension sized vector float list",
    )

    predictions: Optional[Dict[str, AnnotationDB]] = Field(
        None,
        description="Provide the prediction info as a key-value dictionary."
        "The key will represent the agent ant the value the prediction."
        "Using this way you can skip passing the agent inside of the prediction",
    )
    annotations: Optional[Dict[str, AnnotationDB]] = Field(
        None,
        description="Provide the annotation info as a key-value dictionary."
        "The key will represent the agent ant the value the annotation."
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

    @root_validator()
    def prepare_record_for_db(cls, values):
        values = cls.update_annotation(values, "prediction")
        values = cls.update_annotation(values, "annotation")

        return values

    @validator("id", always=True, pre=True)
    def default_id_if_none_provided(cls, id: Optional[str]) -> str:
        """Validates id info and sets a random uuid if not provided"""
        if id is None:
            return str(uuid4())
        return id

    @validator("status", always=True)
    def fill_default_value(cls, status: TaskStatus):
        """Fastapi validator for set default task status"""
        return TaskStatus.default if status is None else status

    @validator("metadata", pre=True)
    def flatten_metadata(cls, metadata: Dict[str, Any]):
        """
        A fastapi validator for flatten metadata dictionary

        Parameters
        ----------
        metadata:
            The metadata dictionary

        Returns
        -------
            A flatten version of metadata dictionary

        """
        if metadata:
            metadata = flatten_dict(metadata, drop_empty=True)
            new_metadata = limit_value_length(
                data=metadata,
                max_length=settings.metadata_field_length,
            )

            if metadata != new_metadata:
                message = (
                    "Some metadata values exceed the max length. Those values will be"
                    f" truncated by keeping only the last {settings.metadata_field_length} characters. "
                    + _messages.ARGILLA_METADATA_FIELD_WARNING_MESSAGE
                )
                warnings.warn(message, UserWarning)
                metadata = new_metadata
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
