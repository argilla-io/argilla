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
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator
from rubrix.server.datasets.model import UpdateDatasetRequest
from rubrix.server.tasks.commons.api.model import (
    BaseAnnotation,
    BaseRecord,
    BaseSearchResults,
    BaseSearchResultsAggregations,
    PredictionStatus,
    ScoreRange,
    SortableField,
    TaskStatus,
    TaskType,
)


class ExtendedEsRecordDataFieldNames(str, Enum):
    text_predicted = "text_predicted"
    text_annotated = "text_annotated"


class Text2TextPrediction(BaseModel):
    """Represents a text prediction/annotation and its score"""

    text: str
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class Text2TextAnnotation(BaseAnnotation):
    """
    Annotation class for text2text tasks

    Attributes:
    -----------

    sentences: str
        List of sentence predictions/annotations

    """

    @validator("sentences")
    def sort_sentences_by_score(cls, sentences: List[Text2TextPrediction]):
        """Sort provided sentences by score desc"""
        return sorted(sentences, key=lambda x: x.score, reverse=True)

    sentences: List[Text2TextPrediction]


class CreationText2TextRecord(BaseRecord[Text2TextAnnotation]):
    """
    Text2Text record

    Attributes:
    -----------

    text:
        The input data text
    """

    text: str

    @classmethod
    def task(cls) -> TaskType:
        """The task type"""
        return TaskType.text2text

    @property
    def predicted(self) -> Optional[PredictionStatus]:
        """Won't apply"""
        return None

    @property
    def words(self) -> str:
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

    @validator("text")
    def validate_text(cls, text: Dict[str, Any]):
        """Applies validation over input text"""
        assert len(text) > 0, "No text provided"
        return text


class Text2TextRecordDB(CreationText2TextRecord):
    """
    The db text2text task record

    Attributes:
    -----------

    last_updated: datetime
        Last record update (read only)
    predicted: Optional[PredictionStatus]
        The record prediction status. Optional
    """

    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")

    def extended_fields(self) -> Dict[str, Any]:
        return {
            ExtendedEsRecordDataFieldNames.text_predicted: self.predicted_as,
            ExtendedEsRecordDataFieldNames.text_annotated: self.annotated_as,
        }


class Text2TextRecord(Text2TextRecordDB):
    """
    The output text2text task record
    """

    def extended_fields(self) -> Dict[str, Any]:
        return {}


class Text2TextBulkData(UpdateDatasetRequest):
    """
    API bulk data for text2text

    Attributes:
    -----------

    records: List[CreationText2TextRecord]
        The text2text record list

    """

    records: List[CreationText2TextRecord]


class Text2TextQuery(BaseModel):
    """
    API Filters for text2text

    Attributes:
    -----------
    ids: Optional[List[Union[str, int]]]
        Record ids list

    query_text: str
        Text query over input text

    annotated_by: List[str]
        List of annotation agents
    predicted_by: List[str]
        List of predicted agents

    status: List[TaskStatus]
        List of task status

    metadata: Optional[Dict[str, Union[str, List[str]]]]
        Text query over metadata fields. Default=None

    predicted: Optional[PredictionStatus]
        The task prediction status

    """

    ids: Optional[List[Union[str, int]]]

    query_text: str = Field(default=None)

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    score: Optional[ScoreRange] = Field(default=None)

    status: List[TaskStatus] = Field(default_factory=list)

    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None


class Text2TextSearchRequest(BaseModel):
    """
    API SearchRequest request

    Attributes:
    -----------

    query: Text2TextQuery
        The search query configuration

    sort:
        The sort order list
    """

    query: Text2TextQuery = Field(default_factory=Text2TextQuery)
    sort: List[SortableField] = Field(default_factory=list)


class Text2TextSearchAggregations(BaseSearchResultsAggregations):
    """
    Extends base aggregation with predicted and annotated text

    Attributes:
    -----------
    predicted_text: Dict[str, int]
        The word cloud aggregations for predicted text
    annotated_text: Dict[str, int]
        The word cloud aggregations for annotated text
    """

    predicted_text: Dict[str, int] = Field(default_factory=dict)
    annotated_text: Dict[str, int] = Field(default_factory=dict)


class Text2TextSearchResults(
    BaseSearchResults[Text2TextRecord, Text2TextSearchAggregations]
):
    pass
