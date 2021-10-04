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

from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from rubrix.client.models import TextClassificationRecord
from rubrix.client.models import TokenAttributions as ClientTokenAttributions
from rubrix.client.sdk.commons.models import BaseAnnotation
from rubrix.client.sdk.commons.models import BaseRecord
from rubrix.client.sdk.commons.models import PredictionStatus
from rubrix.client.sdk.commons.models import ScoreRange
from rubrix.client.sdk.commons.models import TaskStatus
from rubrix.client.sdk.commons.models import UpdateDatasetRequest


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

    def to_client(self) -> TextClassificationRecord:
        """Returns the client model"""
        annotations = (
            [label.class_label for label in self.annotation.labels]
            if self.annotation
            else None
        )
        if annotations and not self.multi_label:
            annotations = annotations[0]

        return TextClassificationRecord(
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
        )

    @classmethod
    def from_client(cls, record: TextClassificationRecord):
        model_dict = {
            "inputs": record.inputs,
            "multi_label": record.multi_label,
            "status": record.status,
        }
        if record.prediction is not None:
            model_dict["prediction"] = {
                "agent": record.prediction_agent,
                "labels": [
                    {"class": label, "score": score}
                    for label, score in record.prediction
                ],
            }
        if record.annotation is not None:
            annotations = (
                record.annotation
                if isinstance(record.annotation, list)
                else [record.annotation]
            )
            gold_labels = [{"class": label, "score": 1.0} for label in annotations]
            model_dict["annotation"] = {
                "agent": record.annotation_agent,
                "labels": gold_labels,
            }
            model_dict["status"] = record.status or "Validated"
        if record.explanation is not None:
            model_dict["explanation"] = {
                key: [attribution.dict() for attribution in value]
                for key, value in record.explanation.items()
            }
        if record.id is not None:
            model_dict["id"] = record.id
        if record.metadata is not None:
            model_dict["metadata"] = record.metadata
        if record.event_timestamp is not None:
            model_dict["event_timestamp"] = record.event_timestamp.isoformat()

        return cls(**model_dict)


class TextClassificationBulkData(UpdateDatasetRequest):
    records: List[CreationTextClassificationRecord]


class TextClassificationQuery(BaseModel):
    ids: Optional[List[Union[str, int]]]

    query_text: str = Field(default=None, alias="query_inputs")
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    status: List[TaskStatus] = Field(default_factory=list)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)
