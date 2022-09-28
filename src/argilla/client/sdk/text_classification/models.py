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

from pydantic import BaseModel, Field

from argilla.client.models import (
    TextClassificationRecord as ClientTextClassificationRecord,
)
from argilla.client.models import TokenAttributions as ClientTokenAttributions
from argilla.client.sdk.commons.models import (
    MACHINE_NAME,
    BaseAnnotation,
    BaseRecord,
    PredictionStatus,
    ScoreRange,
    TaskStatus,
    UpdateDatasetRequest,
)


class ClassPrediction(BaseModel):
    class_label: Union[str, int] = Field(alias="class")
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class TextClassificationAnnotation(BaseAnnotation):
    labels: List[ClassPrediction]


class TokenAttributions(BaseModel):
    token: str
    attributions: Dict[str, float] = Field(default_factory=dict)


class CreationTextClassificationRecord(BaseRecord[TextClassificationAnnotation]):
    inputs: Dict[str, Union[str, List[str]]]
    multi_label: bool = False
    explanation: Optional[Dict[str, List[TokenAttributions]]] = None

    @classmethod
    def from_client(cls, record: ClientTextClassificationRecord):
        prediction = None
        if record.prediction is not None:
            prediction = TextClassificationAnnotation(
                labels=[
                    ClassPrediction(**{"class": label, "score": score})
                    for label, score in record.prediction
                ],
                agent=record.prediction_agent or MACHINE_NAME,
            )

        annotation = None
        if record.annotation is not None:
            annotation_list = (
                record.annotation
                if isinstance(record.annotation, list)
                else [record.annotation]
            )
            annotation = TextClassificationAnnotation(
                labels=[
                    ClassPrediction(**{"class": label}) for label in annotation_list
                ],
                agent=record.annotation_agent or MACHINE_NAME,
            )

        return cls(
            inputs=record.inputs,
            prediction=prediction,
            annotation=annotation,
            multi_label=record.multi_label,
            status=record.status,
            explanation=record.explanation,
            id=record.id,
            metadata=record.metadata,
            event_timestamp=record.event_timestamp,
        )


class TextClassificationRecord(CreationTextClassificationRecord):
    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")

    def to_client(self) -> ClientTextClassificationRecord:
        """Returns the client model"""
        annotations = (
            [label.class_label for label in self.annotation.labels]
            if self.annotation
            else None
        )
        if annotations and not self.multi_label:
            annotations = annotations[0]

        return ClientTextClassificationRecord(
            id=self.id,
            event_timestamp=self.event_timestamp,
            inputs=self.inputs,
            multi_label=self.multi_label,
            status=self.status,
            metadata=self.metadata or {},
            prediction=[
                (label.class_label, label.score) for label in self.prediction.labels
            ]
            if self.prediction
            else None,
            prediction_agent=self.prediction.agent if self.prediction else None,
            annotation=annotations,
            annotation_agent=self.annotation.agent if self.annotation else None,
            explanation={
                key: [
                    ClientTokenAttributions.parse_obj(attribution)
                    for attribution in attributions
                ]
                for key, attributions in self.explanation.items()
            }
            if self.explanation
            else None,
            metrics=self.metrics or None,
            search_keywords=self.search_keywords or None,
        )


class TextClassificationBulkData(UpdateDatasetRequest):
    records: List[CreationTextClassificationRecord]


class TextClassificationQuery(BaseModel):
    ids: Optional[List[Union[str, int]]]

    query_text: str = Field(default=None)
    advanced_query_dsl: bool = False
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    status: List[TaskStatus] = Field(default_factory=list)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)

    uncovered_by_rules: List[str] = Field(
        default_factory=list,
        description="List of rule queries that WILL NOT cover the resulting records",
    )


class LabelingRule(BaseModel):
    """
    Adds read-only attributes to the labeling rule

    Attributes:
    -----------

    query:
        The ES query of the rule

    label: str
        The label associated with the rule

    description:
        A brief description of the rule

    author:
        Who created the rule

    created_at:
        When was the rule created

    """

    label: str = None
    labels: List[str] = Field(default_factory=list)
    query: str
    description: Optional[str] = None
    author: str
    created_at: datetime = None


class LabelingRuleMetricsSummary(BaseModel):
    """Metrics generated for a labeling rule"""

    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None
    correct: Optional[float] = None
    incorrect: Optional[float] = None
    precision: Optional[float] = None

    total_records: int
    annotated_records: int
