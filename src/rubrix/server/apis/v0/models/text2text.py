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
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from rubrix.server.apis.v0.models.commons.model import (
    BaseAnnotation,
    BaseRecord,
    PredictionStatus,
    SortableField,
)
from rubrix.server.apis.v0.models.datasets import UpdateDatasetRequest
from rubrix.server.apis.v0.models.metrics.commons import CommonTasksMetrics
from rubrix.server.commons.models import TaskType
from rubrix.server.services.search.model import BaseSearchResults
from rubrix.server.services.tasks.text2text.models import (
    Text2TextDatasetDB as _Text2TextDatasetDB,
)
from rubrix.server.services.tasks.text2text.models import (
    Text2TextQuery as _Text2TextQuery,
)
from rubrix.server.services.tasks.text2text.models import (
    Text2TextSearchAggregations as _Text2TextSearchAggregations,
)


class Text2TextPrediction(BaseModel):
    text: str
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class Text2TextAnnotation(BaseAnnotation):
    @validator("sentences")
    def sort_sentences_by_score(cls, sentences: List[Text2TextPrediction]):
        """Sort provided sentences by score desc"""
        return sorted(sentences, key=lambda x: x.score, reverse=True)

    sentences: List[Text2TextPrediction]


class CreationText2TextRecord(BaseRecord[Text2TextAnnotation]):

    text: str

    @classmethod
    def task(cls) -> TaskType:
        """The task type"""
        return TaskType.text2text

    def all_text(self) -> str:
        return self.text


class Text2TextRecord(CreationText2TextRecord):
    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")

    def extended_fields(self):
        return {}


class Text2TextBulkData(UpdateDatasetRequest):
    records: List[CreationText2TextRecord]


class Text2TextQuery(_Text2TextQuery):
    pass


class Text2TextSearchAggregations(_Text2TextSearchAggregations):
    pass


class Text2TextSearchResults(
    BaseSearchResults[Text2TextRecord, Text2TextSearchAggregations]
):
    pass


class Text2TextDatasetDB(_Text2TextDatasetDB):
    pass


class Text2TextMetrics(CommonTasksMetrics[Text2TextRecord]):
    pass


class Text2TextSearchRequest(BaseModel):
    query: Text2TextQuery = Field(default_factory=Text2TextQuery)
    sort: List[SortableField] = Field(default_factory=list)
