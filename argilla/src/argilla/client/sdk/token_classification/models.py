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

from argilla._constants import DEFAULT_MAX_KEYWORD_LENGTH
from argilla.client.models import TokenClassificationRecord as ClientTokenClassificationRecord
from argilla.client.sdk.commons.models import (
    MACHINE_NAME,
    BaseAnnotation,
    BaseRecord,
    PredictionStatus,
    ScoreRange,
    SdkVectorSearch,
    TaskStatus,
    UpdateDatasetRequest,
)
from argilla.pydantic_v1 import BaseModel, Field, validator


class EntitySpan(BaseModel):
    start: int
    end: int
    label: str = Field(min_length=1, max_length=DEFAULT_MAX_KEYWORD_LENGTH)
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class TokenClassificationAnnotation(BaseAnnotation):
    entities: List[EntitySpan] = Field(default_factory=list)
    score: Optional[float] = None


class CreationTokenClassificationRecord(BaseRecord[TokenClassificationAnnotation]):
    tokens: List[str] = Field(min_items=1)

    text: str

    @validator("text")
    def check_text_content(cls, text: str):
        assert text and text.strip(), "No text or empty text provided"
        return text

    @classmethod
    def from_client(cls, record: ClientTokenClassificationRecord):
        prediction = None
        if record.prediction is not None:
            prediction = TokenClassificationAnnotation(
                entities=[
                    EntitySpan(label=ent[0], start=ent[1], end=ent[2])
                    if len(ent) == 3
                    else EntitySpan(label=ent[0], start=ent[1], end=ent[2], score=ent[3])
                    for ent in record.prediction
                ],
                agent=record.prediction_agent or MACHINE_NAME,
            )

        annotation = None
        if record.annotation is not None:
            annotation = TokenClassificationAnnotation(
                entities=[EntitySpan(label=ent[0], start=ent[1], end=ent[2]) for ent in record.annotation],
                agent=record.annotation_agent or MACHINE_NAME,
            )

        return cls(
            tokens=record.tokens,
            text=record.text,
            prediction=prediction,
            annotation=annotation,
            vectors=cls._from_client_vectors(record.vectors),
            status=record.status,
            id=record.id,
            metadata=record.metadata,
            event_timestamp=record.event_timestamp,
        )


class TokenClassificationRecord(CreationTokenClassificationRecord):
    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")

    def to_client(self) -> ClientTokenClassificationRecord:
        return ClientTokenClassificationRecord(
            text=self.text,
            tokens=self.tokens,
            prediction=[(ent.label, ent.start, ent.end, ent.score) for ent in self.prediction.entities]
            if self.prediction
            else None,
            prediction_agent=self.prediction.agent if self.prediction else None,
            annotation=[(ent.label, ent.start, ent.end) for ent in self.annotation.entities]
            if self.annotation
            else None,
            annotation_agent=self.annotation.agent if self.annotation else None,
            vectors=self._to_client_vectors(self.vectors),
            id=self.id,
            event_timestamp=self.event_timestamp,
            status=self.status,
            metadata=self.metadata or {},
            metrics=self.metrics or None,
            search_keywords=self.search_keywords or None,
        )


class TokenClassificationBulkData(UpdateDatasetRequest):
    records: List[CreationTokenClassificationRecord]


class TokenClassificationQuery(BaseModel):
    ids: Optional[List[Union[str, int]]]

    query_text: str = Field(default=None)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    status: List[TaskStatus] = Field(default_factory=list)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)

    vector: Optional[SdkVectorSearch] = Field(default=None)
