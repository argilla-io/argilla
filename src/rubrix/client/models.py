import dataclasses
import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class TaskStatus(str, Enum):
    """
    Task data status:

    **Default**, default status, for no provided status records.
    **Edited**, normally used when original annotation was modified but not yet validated (confirmed).
    **Discarded**, for records that will be excluded for analysis.
    **Validated**, when annotation was confirmed as ok.

    """

    DEFAULT = "Default"
    EDITED = "Edited"
    DISCARDED = "Discarded"
    VALIDATED = "Validated"


class AsDictMixin:
    """Dataclases mixin for easy object2dict operation"""

    def asdict(self) -> Dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v}


@dataclass
class BulkResponse:
    """Data info for bulk results

    Attributes:
    -----------

    dataset:
        The dataset name
    processed:
        Number of records in bulk
    failed:
        Number of failed records
    """

    dataset: str
    processed: int
    failed: Optional[int] = 0


@dataclass
class DatasetSnapshot:
    """The dataset snapshot info"""

    id: str
    task: str
    creation_date: datetime.datetime


@dataclass
class ClassPrediction:
    """Single class prediction

    Attributes:
    -----------

    class_label: Union[str, int]
        the predicted class

    confidence: float
        the predicted class confidence. For human-supervised annotations,
        this probability should be 1.0
    """

    class_label: Union[str, int]
    confidence: Optional[float] = 1.0


@dataclass
class TextClassificationAnnotation:
    """Annotation class for text classification tasks

    Attributes:
    -----------
    agent: str
        the annotation agent
    labels: List[LabelPrediction]
        list of annotated labels with confidence
    """

    agent: str
    labels: List[ClassPrediction]


@dataclass
class TokenAttributions:
    """The token attributions explaining predicted labels

    Attributes:
    -----------

    token: str
        The input token
    attributions: Dict[str, float]
        A dictionary containing label class-attribution pairs
    """

    token: str
    attributions: Dict[str, float] = dataclasses.field(default_factory=dict)


@dataclass
class TextClassificationRecord(AsDictMixin):
    """Record for text classification"""

    inputs: Dict[str, Any]

    prediction: Optional[TextClassificationAnnotation] = None
    annotation: Optional[TextClassificationAnnotation] = None
    multi_label: Optional[bool] = False

    explanation: Optional[Dict[str, List[TokenAttributions]]] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = dataclasses.field(default_factory=dict)
    status: Optional[TaskStatus] = None
    event_timestamp: Optional[datetime.datetime] = None


@dataclass
class EntitySpan:
    """The tokens span for a labeled text.

    Entity spans will be defined between from start to end - 1

    Attributes:
    -----------

    start: int
        character start position
    end: int
        character end position
    start_token: Optional[int]
        start token for entity span. Optional
    end_token: Optional[int]
        end token for entity span. Optional
    label: str
        the label related to tokens that conforms the entity span"""

    start: int
    end: int
    label: str
    start_token: Optional[int] = None
    end_token: Optional[int] = None


@dataclass
class TokenClassificationAnnotation:
    """Annotation class for Token classification problem

    Attributes:
    -----------
    entities: List[EntitiesSpan]
        a list of detected entities spans in tokenized text, if any.
    score: float
        score related to annotated entities. The higher is score value, the
        more likely is that entities were properly annotated."""

    agent: str
    entities: Optional[List[EntitySpan]] = None
    score: Optional[float] = None


@dataclass
class TokenClassificationRecord(AsDictMixin):
    """Record for token classification"""

    tokens: List[str]
    raw_text: Optional[str] = None
    prediction: Optional[TokenClassificationAnnotation] = None
    annotation: Optional[TokenClassificationAnnotation] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = dataclasses.field(default_factory=dict)
    status: Optional[TaskStatus] = None
    event_timestamp: Optional[datetime.datetime] = None


Record = Union[TextClassificationRecord, TokenClassificationRecord]
