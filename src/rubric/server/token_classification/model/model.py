from datetime import datetime
from typing import List, Optional, Set

from pydantic import BaseModel, Field, root_validator, validator
from rubric.server.commons.models import (
    BaseAnnotation,
    BaseRecord,
    PredictionStatus,
    RecordTaskInfo,
    TaskType,
)


class EntitySpan(BaseModel):
    """
    The tokens span for a labeled text.

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
        the label related to tokens that conforms the entity span
    """

    start: int
    end: int
    start_token: Optional[int] = None
    end_token: Optional[int] = None
    label: str

    @validator("end")
    def check_span_offset(cls, end: int, values):
        """Validates span offset"""
        assert end > values["start"]
        return end

    @validator("end_token")
    def check_token_span_offset(cls, end_token: int, values):
        """Validates token span offset"""
        start_token = values["start_token"]
        if start_token is not None and end_token is not None:
            assert end_token > start_token
        return end_token

    def __hash__(self):
        return hash(type(self)) + hash(self.__dict__.values())


class TokenClassificationAnnotation(BaseAnnotation):
    """
    Annotation class for rToken classification problem

    Attributes:
    -----------
    entities: List[EntitiesSpan]
        a list of detected entities spans in tokenized text, if any.
    score: float
        score related to annotated entities. The higher is score value, the
        more likely is that entities were properly annotated.
    """

    entities: List[EntitySpan] = Field(default_factory=list)
    score: Optional[float] = None


class TokenClassificationTask(RecordTaskInfo[TokenClassificationAnnotation]):
    """
    Task info for token classification

    """

    @classmethod
    def task(cls) -> TaskType:
        """The record task type"""
        return TaskType.token_classification

    @property
    def predicted(self) -> Optional[PredictionStatus]:
        if self.annotation and self.prediction:
            return (
                PredictionStatus.OK
                if self.annotation.entities == self.prediction.entities
                else PredictionStatus.KO
            )
        return None

    @property
    def predicted_as(self) -> List[str]:
        return [ent.label for ent in self._predicted_entities()]

    @property
    def annotated_as(self) -> List[str]:
        return [ent.label for ent in self._entities()]

    def _entities(self) -> Set[EntitySpan]:
        """Shortcut for real annotated entities, if provided"""
        if self.annotation is None:
            return set()
        return set(self.annotation.entities)

    def _predicted_entities(self) -> Set[EntitySpan]:
        """Predicted entities"""
        if self.prediction is None:
            return set()
        return set(self.prediction.entities)


class CreationTokenClassificationRecord(BaseRecord, TokenClassificationTask):
    """
    Dataset record for token classification task

    Attributes:
    -----------

    tokens: List[str]
        The input tokens
    raw_text: Optional[str]
        Textual representation of token list

    """

    tokens: List[str]
    raw_text: Optional[str]

    @root_validator
    def check_prediction_integrity(cls, values):
        """Validates prediction entities in terms of offset spans"""
        if values.get("prediction") is None:
            return values
        raw_text = values.get("raw_tex")
        raw_text = raw_text or " ".join(values.get("tokens", []))
        prediction = values["prediction"]
        for entity in prediction.entities:
            assert (
                len(raw_text[entity.start : entity.end]) > 1
            ), "Entities definition out of index"

        return values

    class Config:
        allow_population_by_field_name = True


class TokenClassificationRecord(CreationTokenClassificationRecord):
    """
    The main token classification task record

    Attributes:
    -----------

    last_updated: datetime
        Last record update (read only)
    predicted: Optional[PredictionStatus]
        The record prediction status. Optional
    """

    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")
