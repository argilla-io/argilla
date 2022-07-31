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
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.backend.search.model import BackendRecordsQuery
from rubrix.server.backend.search.model import BaseRecordsQuery as _BaseSearchQuery
from rubrix.server.backend.search.model import SortConfig
from rubrix.server.commons.models import TaskStatus, TaskType
from rubrix.server.helpers import flatten_dict
from rubrix.utils import limit_value_length


class BaseSearchQuery(_BaseSearchQuery):
    pass


class RecordSearch(BaseModel):
    """
    Dao search

    Attributes:
    -----------

    query:
        The search query portion
    sort:
        The sort order
    """

    query: Optional[BackendRecordsQuery] = None
    sort: SortConfig = Field(default_factory=SortConfig)


class RecordSearchResults(BaseModel):
    """
    Dao search results

    Attributes:
    -----------

    total: int
        The total of query results
    records: List[T]
        List of records retrieved for the pagination configuration
    """

    total: int
    records: List[Dict[str, Any]]


class EsRecordDataFieldNames(str, Enum):

    predicted_as = "predicted_as"
    annotated_as = "annotated_as"
    annotated_by = "annotated_by"
    predicted_by = "predicted_by"
    status = "status"
    predicted = "predicted"
    score = "score"
    words = "words"
    event_timestamp = "event_timestamp"
    last_updated = "last_updated"

    def __str__(self):
        return self.value


class BaseAnnotation(BaseModel):
    agent: str = Field(max_length=64)


class PredictionStatus(str, Enum):
    OK = "ok"
    KO = "ko"


DAOAnnotation = TypeVar("DAOAnnotation", bound=BaseAnnotation)


class BaseRecordDB(GenericModel, Generic[DAOAnnotation]):

    id: Optional[Union[int, str]] = Field(default=None)
    metadata: Dict[str, Any] = Field(default=None)
    event_timestamp: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    prediction: Optional[DAOAnnotation] = None
    annotation: Optional[DAOAnnotation] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    search_keywords: Optional[List[str]] = None

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

    @validator("search_keywords")
    def remove_duplicated_keywords(cls, value) -> List[str]:
        """Remove duplicated keywords"""
        if value:
            return list(set(value))

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
            metadata = limit_value_length(metadata, max_length=MAX_KEYWORD_LENGTH)
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
            EsRecordDataFieldNames.predicted: self.predicted,
            EsRecordDataFieldNames.annotated_as: self.annotated_as,
            EsRecordDataFieldNames.predicted_as: self.predicted_as,
            EsRecordDataFieldNames.annotated_by: self.annotated_by,
            EsRecordDataFieldNames.predicted_by: self.predicted_by,
            EsRecordDataFieldNames.score: self.scores,
        }

    def dict(self, *args, **kwargs) -> "DictStrAny":
        """
        Extends base component dict extending object properties
        and user defined extended fields
        """
        return {
            **super().dict(*args, **kwargs),
            **self.extended_fields(),
        }


DAORecordDB = TypeVar("DAORecordDB", bound=BaseRecordDB)
