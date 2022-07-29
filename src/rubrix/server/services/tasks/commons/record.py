from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from rubrix.server.commons.models import TaskStatus, TaskType


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


Annotation = TypeVar("Annotation", bound=BaseAnnotation)


class BaseRecordDB(GenericModel, Generic[Annotation]):

    id: Optional[Union[int, str]] = Field(default=None)
    metadata: Dict[str, Any] = Field(default=None)
    event_timestamp: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    prediction: Optional[Annotation] = None
    annotation: Optional[Annotation] = None
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


Record = TypeVar("Record", bound=BaseRecordDB)
