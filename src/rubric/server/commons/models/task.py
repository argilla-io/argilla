"""
Common model for task definitions
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel
from rubric.server.commons.helpers import flatten_dict


class BaseRecord(BaseModel):
    """
    Minimal dataset record information

    Attributes
    ----------

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

    @validator("metadata")
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
            return flatten_dict(metadata)
        return metadata


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


T = TypeVar("T", bound=BaseAnnotation)


class RecordTaskInfo(GenericModel, Generic[T]):
    """
    Base class for task data info at record level

    Attributes
    ----------

    status:
        The task status
    prediction:
        The task prediction info
    annotation:
        The task annotation info
    """

    status: Optional[TaskStatus] = None
    prediction: Optional[T] = None
    annotation: Optional[T] = None

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
        more properties than commons (predicted, annotated_as,....) could implement
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
            "predicted": self.predicted,
            "annotated_as": self.annotated_as,
            "predicted_as": self.predicted_as,
            "annotated_by": self.annotated_by,
            "predicted_by": self.predicted_by,
            **self.extended_fields(),
        }
