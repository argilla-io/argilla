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
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from argilla.server.apis.v0.models.commons.model import (
    BaseAnnotation,
    BaseRecord,
    BaseRecordInputs,
    BaseSearchResults,
    ScoreRange,
    SortableField,
)
from argilla.server.apis.v0.models.datasets import UpdateDatasetRequest
from argilla.server.commons.models import PredictionStatus, TaskType
from argilla.server.services.metrics.models import CommonTasksMetrics
from argilla.server.services.search.model import (
    ServiceBaseRecordsQuery,
    ServiceBaseSearchResultsAggregations,
)
from argilla.server.services.tasks.text2text.models import ServiceText2TextDataset


class Text2TextPrediction(BaseModel):
    text: str
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class Text2TextAnnotation(BaseAnnotation):
    @validator("sentences")
    def sort_sentences_by_score(cls, sentences: List[Text2TextPrediction]):
        """Sort provided sentences by score desc"""
        return sorted(sentences, key=lambda x: x.score, reverse=True)

    sentences: List[Text2TextPrediction]


class Text2TextRecordInputs(BaseRecordInputs[Text2TextAnnotation]):

    text: str


class Text2TextRecord(Text2TextRecordInputs, BaseRecord[Text2TextAnnotation]):
    pass


class Text2TextBulkRequest(UpdateDatasetRequest):
    records: List[Text2TextRecordInputs]


class Text2TextQuery(ServiceBaseRecordsQuery):
    score: Optional[ScoreRange] = Field(default=None)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)


class Text2TextSearchAggregations(ServiceBaseSearchResultsAggregations):
    predicted_text: Dict[str, int] = Field(default_factory=dict)
    annotated_text: Dict[str, int] = Field(default_factory=dict)


class Text2TextSearchResults(
    BaseSearchResults[Text2TextRecord, Text2TextSearchAggregations]
):
    pass


class Text2TextDataset(ServiceText2TextDataset):
    pass


class Text2TextMetrics(CommonTasksMetrics[Text2TextRecord]):
    pass


class Text2TextSearchRequest(BaseModel):
    query: Text2TextQuery = Field(default_factory=Text2TextQuery)
    sort: List[SortableField] = Field(default_factory=list)
