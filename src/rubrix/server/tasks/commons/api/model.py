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

"""
Common model for task definitions
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from fastapi import Query
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.commons.helpers import flatten_dict, limit_value_length
from rubrix.server.metrics.model import DatasetMetricResults


class EsRecordDataFieldNames(str, Enum):
    """Common elasticsearch field names"""

    predicted_as = "predicted_as"
    annotated_as = "annotated_as"
    annotated_by = "annotated_by"
    predicted_by = "predicted_by"
    status = "status"
    predicted = "predicted"
    score = "score"
    words = "words"
    event_timestamp = "event_timestamp"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class SortableField(BaseModel):
    """Sortable field structure"""

    id: str
    order: SortOrder = SortOrder.asc


class BulkResponse(BaseModel):
    """
    Data info for bulk results

    Attributes
    ----------

    dataset:
        The dataset name
    processed:
        Number of records in bulk
    failed:
        Number of failed records
    """

    dataset: str
    processed: int
    failed: int = 0


@dataclass
class PaginationParams:
    """Query pagination params"""

    limit: int = Query(50, gte=0, le=1000, description="Response records limit")
    from_: int = Query(
        0, ge=0, le=10000, alias="from", description="Record sequence from"
    )


class BaseAnnotation(BaseModel):
    """
    Annotation class base

    Attributes:
    -----------

    agent:
        Which agent or component makes the annotation. We should find model annotations, user annotations,
        or some other human-supervised automatic process.
    """

    agent: str


class TaskType(str, Enum):
    """
    The available task types:

    **text_classification**, for text classification tasks
    **token_classification**, for token classification tasks

    """

    text_classification = "TextClassification"
    token_classification = "TokenClassification"
    text2text = "Text2Text"
    multi_task_text_token_classification = "MultitaskTextTokenClassification"


class TaskStatus(str, Enum):
    """
    Task data status:

    **Default**, default status, for no provided status records.
    **Edited**, normally used when original annotation was modified but not yet validated (confirmed).
    **Discarded**, for records that will be excluded for analysis.
    **Validated**, when annotation was confirmed as ok.

    """

    default = "Default"
    edited = "Edited"
    discarded = "Discarded"
    validated = "Validated"


class PredictionStatus(str, Enum):
    """
    The prediction status:

    **OK**, for record containing a success prediction
    **KO**, for record containing a wrong prediction

    """

    OK = "ok"
    KO = "ko"


Annotation = TypeVar("Annotation", bound=BaseAnnotation)


class BaseRecord(GenericModel, Generic[Annotation]):
    """
    Minimal dataset record information

    Attributes:
    -----------

    id:
        The record id
    metadata:
        The metadata related to record
    event_timestamp:
        The timestamp when record event was triggered

    """

    id: Optional[Union[int, str]] = Field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = Field(default=None)
    event_timestamp: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    prediction: Optional[Annotation] = None
    annotation: Optional[Annotation] = None

    @validator("id", always=True)
    def default_id_if_none_provided(cls, id: Optional[str]) -> str:
        """Validates id info and sets a random uuid if not provided"""
        if id is None:
            return str(uuid4())
        return id

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
            metadata = flatten_dict(metadata)
            metadata = limit_value_length(metadata, max_length=MAX_KEYWORD_LENGTH)
        return metadata

    @validator("status", always=True)
    def fill_default_value(cls, status: TaskStatus):
        """Fastapi validator for set default task status"""
        return TaskStatus.default if status is None else status

    @classmethod
    def task(cls) -> TaskType:
        """The task type related to this task info"""
        raise NotImplementedError

    @property
    def predicted(self) -> Optional[PredictionStatus]:
        """The task record prediction status (if any)"""
        raise NotImplementedError

    @property
    def predicted_as(self) -> List[str]:
        """Predictions strings representation"""
        raise NotImplementedError

    @property
    def annotated_as(self) -> List[str]:
        """Annotations strings representation"""
        raise NotImplementedError

    @property
    def scores(self) -> List[float]:
        """Prediction scores"""
        raise NotImplementedError

    @property
    def words(self) -> str:
        """
        Textual information related to record.
        This info will be used analytical data purposes (word tags, word distributions,...)
        """
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
        return {}

    def dict(self, *args, **kwargs) -> "DictStrAny":
        """
        Extends base component dict extending object properties
        and user defined extnded fields
        """
        return {
            **super().dict(*args, **kwargs),
            EsRecordDataFieldNames.predicted: self.predicted,
            EsRecordDataFieldNames.annotated_as: self.annotated_as,
            EsRecordDataFieldNames.predicted_as: self.predicted_as,
            EsRecordDataFieldNames.annotated_by: self.annotated_by,
            EsRecordDataFieldNames.predicted_by: self.predicted_by,
            EsRecordDataFieldNames.score: self.scores,
            EsRecordDataFieldNames.words: self.words,
            **self.extended_fields(),
        }


class BaseSearchResultsAggregations(BaseModel):

    """
    API for result aggregations

    Attributes:
    -----------
    predicted_as: Dict[str, int]
        Occurrence info about more relevant predicted terms
    annotated_as: Dict[str, int]
        Occurrence info about more relevant annotated terms
    annotated_by: Dict[str, int]
        Occurrence info about more relevant annotation agent terms
    predicted_by: Dict[str, int]
        Occurrence info about more relevant prediction agent terms
    status: Dict[str, int]
        Occurrence info about task status
    predicted: Dict[str, int]
        Occurrence info about task prediction status
    words: Dict[str, int]
        The word cloud aggregations
    metadata: Dict[str, Dict[str, Any]]
        The metadata fields aggregations
    """

    predicted_as: Dict[str, int] = Field(default_factory=dict)
    annotated_as: Dict[str, int] = Field(default_factory=dict)
    annotated_by: Dict[str, int] = Field(default_factory=dict)
    predicted_by: Dict[str, int] = Field(default_factory=dict)
    status: Dict[str, int] = Field(default_factory=dict)
    predicted: Dict[str, int] = Field(default_factory=dict)
    score: Dict[str, int] = Field(default_factory=dict)
    words: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


Record = TypeVar("Record", bound=BaseRecord)
Aggregations = TypeVar("Aggregations", bound=BaseSearchResultsAggregations)


class BaseSearchResults(GenericModel, Generic[Record, Aggregations]):
    """
    API search results

    Attributes:
    -----------

    total:
        The total number of records
    records:
        The selected records to return
    aggregations:
        Requested aggregations
    metrics:
        Requested metrics
    """

    total: int = 0
    records: List[Record] = Field(default_factory=list)
    aggregations: Aggregations = None


class ScoreRange(BaseModel):
    """Score range filter"""

    range_from: float = Field(default=0.0, alias="from")
    range_to: float = Field(default=None, alias="to")

    class Config:
        allow_population_by_field_name = True
