from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from rubrix.server.apis.v0.models.metrics.commons import CommonTasksMetrics
from rubrix.server.commons.models import TaskType
from rubrix.server.daos.models.records import BaseAnnotation
from rubrix.server.services.datasets import ServiceBaseDataset
from rubrix.server.services.search.model import (
    BaseSearchResults,
    BaseSearchResultsAggregations,
    ScoreRange,
    ServiceBaseSearchQuery,
    SortableField,
)
from rubrix.server.services.tasks.commons import (
    ServiceBaseRecord,
    ServicePredictionStatus,
)


class Text2TextPrediction(BaseModel):
    text: str
    score: float


class Text2TextAnnotation(BaseAnnotation):
    sentences: List[Text2TextPrediction]


class Text2TextRecordDB(ServiceBaseRecord[Text2TextAnnotation]):
    text: str
    last_updated: datetime = None

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


class Text2TextQuery(ServiceBaseSearchQuery):
    score: Optional[ScoreRange] = Field(default=None)
    predicted: Optional[ServicePredictionStatus] = Field(default=None, nullable=True)


class Text2TextSearchRequest(BaseModel):
    query: Text2TextQuery = Field(default_factory=Text2TextQuery)
    sort: List[SortableField] = Field(default_factory=list)


class Text2TextSearchAggregations(BaseSearchResultsAggregations):
    predicted_text: Dict[str, int] = Field(default_factory=dict)
    annotated_text: Dict[str, int] = Field(default_factory=dict)


class Text2TextSearchResults(
    BaseSearchResults[Text2TextRecordDB, Text2TextSearchAggregations]
):
    pass


class Text2TextDatasetDB(ServiceBaseDataset):
    task: TaskType = Field(default=TaskType.text2text, const=True)
    pass


class Text2TextMetrics(CommonTasksMetrics[Text2TextRecordDB]):
    pass
