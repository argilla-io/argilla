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
from typing import Dict, List, Optional, Union

from argilla_v1.client.models import Text2TextRecord as ClientText2TextRecord
from argilla_v1.client.sdk.commons.models import (
    MACHINE_NAME,
    BaseAnnotation,
    BaseRecord,
    PredictionStatus,
    ScoreRange,
    SdkVectorSearch,
    TaskStatus,
    UpdateDatasetRequest,
)
from argilla_v1.pydantic_v1 import BaseModel, Field


class Text2TextPrediction(BaseModel):
    text: str
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class Text2TextAnnotation(BaseAnnotation):
    sentences: List[Text2TextPrediction]


class CreationText2TextRecord(BaseRecord[Text2TextAnnotation]):
    text: str

    @classmethod
    def from_client(cls, record: ClientText2TextRecord):
        prediction = None
        if record.prediction is not None:
            prediction = Text2TextAnnotation(
                sentences=[
                    Text2TextPrediction(text=pred[0], score=pred[1])
                    if isinstance(pred, tuple)
                    else Text2TextPrediction(text=pred)
                    for pred in record.prediction
                ],
                agent=record.prediction_agent or MACHINE_NAME,
            )
        annotation = None
        if record.annotation is not None:
            annotation = Text2TextAnnotation(
                sentences=[Text2TextPrediction(text=record.annotation)],
                agent=record.annotation_agent or MACHINE_NAME,
            )

        return cls(
            text=record.text,
            prediction=prediction,
            annotation=annotation,
            vectors=cls._from_client_vectors(record.vectors),
            status=record.status,
            metadata=record.metadata,
            id=record.id,
            event_timestamp=record.event_timestamp,
        )


class Text2TextRecord(CreationText2TextRecord):
    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")

    def to_client(self) -> ClientText2TextRecord:
        return ClientText2TextRecord(
            text=self.text,
            prediction=[(sentence.text, sentence.score) for sentence in self.prediction.sentences]
            if self.prediction
            else None,
            prediction_agent=self.prediction.agent if self.prediction else None,
            annotation=self.annotation.sentences[0].text if self.annotation else None,
            annotation_agent=self.annotation.agent if self.annotation else None,
            vectors=self._to_client_vectors(self.vectors),
            status=self.status,
            metadata=self.metadata or {},
            id=self.id,
            event_timestamp=self.event_timestamp,
            metrics=self.metrics or None,
            search_keywords=self.search_keywords or None,
        )


class Text2TextBulkData(UpdateDatasetRequest):
    records: List[CreationText2TextRecord]


class Text2TextQuery(BaseModel):
    ids: Optional[List[Union[str, int]]]

    query_text: str = Field(default=None)

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    vector: Optional[SdkVectorSearch] = Field(default=None)

    score: Optional[ScoreRange] = Field(default=None)

    status: List[TaskStatus] = Field(default_factory=list)

    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None
