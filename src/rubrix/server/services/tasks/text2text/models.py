from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from rubrix.server.commons.models import PredictionStatus, TaskType
from rubrix.server.services.datasets import ServiceBaseDataset
from rubrix.server.services.search.model import (
    ServiceBaseRecordsQuery,
    ServiceBaseSearchResultsAggregations,
    ServiceScoreRange,
    ServiceSearchResults,
)
from rubrix.server.services.tasks.commons import (
    ServiceBaseAnnotation,
    ServiceBaseRecord,
)


class ServiceText2TextPrediction(BaseModel):
    text: str
    score: float


class ServiceText2TextAnnotation(ServiceBaseAnnotation):
    sentences: List[ServiceText2TextPrediction]


class ServiceText2TextRecord(ServiceBaseRecord[ServiceText2TextAnnotation]):
    text: str

    @classmethod
    def task(cls) -> TaskType:
        """The task type"""
        return TaskType.text2text

    def all_text(self) -> str:
        return self.text

    @property
    def predicted_as(self) -> Optional[List[str]]:
        return (
            [sentence.text for sentence in self.prediction.sentences]
            if self.prediction
            else None
        )

    @property
    def annotated_as(self) -> Optional[List[str]]:
        return (
            [sentence.text for sentence in self.annotation.sentences]
            if self.annotation
            else None
        )

    @property
    def scores(self) -> List[float]:
        """Values of prediction scores"""
        if not self.prediction:
            return []
        return [sentence.score for sentence in self.prediction.sentences]

    def extended_fields(self) -> Dict[str, Any]:
        return {
            "annotated_as": self.annotated_as,
            "predicted_as": self.predicted_as,
            "annotated_by": self.annotated_by,
            "predicted_by": self.predicted_by,
            "score": self.scores,
            "words": self.all_text(),
        }


class ServiceText2TextQuery(ServiceBaseRecordsQuery):
    score: Optional[ServiceScoreRange] = Field(default=None)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)


class ServiceText2TextDataset(ServiceBaseDataset):
    task: TaskType = Field(default=TaskType.text2text, const=True)
    pass
