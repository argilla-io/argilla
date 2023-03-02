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

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from argilla.server.commons.models import PredictionStatus, TaskType
from argilla.server.services.datasets import ServiceBaseDataset
from argilla.server.services.search.model import (
    ServiceBaseRecordsQuery,
    ServiceScoreRange,
)
from argilla.server.services.tasks.commons import (
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
        return [sentence.text for sentence in self.prediction.sentences] if self.prediction else None

    @property
    def annotated_as(self) -> Optional[List[str]]:
        return [sentence.text for sentence in self.annotation.sentences] if self.annotation else None

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
        }


class ServiceText2TextQuery(ServiceBaseRecordsQuery):
    score: Optional[ServiceScoreRange] = Field(default=None)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)
