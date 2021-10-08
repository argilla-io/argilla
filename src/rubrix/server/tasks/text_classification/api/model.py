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
from typing import Any, ClassVar, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.commons.helpers import flatten_dict
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


class ClassPrediction(BaseModel):
    """
    Single class prediction

    Attributes:
    -----------

    class_label: Union[str, int]
        the predicted class

    score: float
        the predicted class score. For human-supervised annotations,
        this probability should be 1.0
    """

    class_label: Union[str, int] = Field(alias="class")
    score: float = Field(default=1.0, ge=0.0, le=1.0)

    @validator("class_label")
    def check_label_length(cls, class_label):
        if isinstance(class_label, str):
            assert 1 <= len(class_label) <= MAX_KEYWORD_LENGTH, (
                f"Class name '{class_label}' exceeds max length of {MAX_KEYWORD_LENGTH}"
                if len(class_label) > MAX_KEYWORD_LENGTH
                else f"Class name must not be empty"
            )
        return class_label

    # See <https://pydantic-docs.helpmanual.io/usage/model_config>
    class Config:
        allow_population_by_field_name = True


class TextClassificationAnnotation(BaseAnnotation):
    """
    Annotation class for text classification tasks

    Attributes:
    -----------

    labels: List[LabelPrediction]
        list of annotated labels with score
    """

    labels: List[ClassPrediction]

    @validator("labels")
    def sort_labels(cls, labels: List[ClassPrediction]):
        """Sort provided labels by score"""
        return sorted(labels, key=lambda x: x.score, reverse=True)


class TokenAttributions(BaseModel):
    """
    The token attributions explaining predicted labels

    Attributes:
    -----------

    token: str
        The input token
    attributions: Dict[str, float]
        A dictionary containing label class-attribution pairs

    """

    token: str
    attributions: Dict[str, float] = Field(default_factory=dict)


class CreationTextClassificationRecord(BaseRecord[TextClassificationAnnotation]):
    """
    Text classification record

    Attributes:
    -----------

    inputs: Dict[str, Union[str, List[str]]]
        The input data text

    multi_label: bool
        Enable text classification with multiple predicted/annotated labels.
        Default=False

    explanation: Dict[str, List[TokenAttributions]]
        Token attribution list explaining predicted classes per token input.
        The dictionary key must be aligned with provided record text. Optional
    """

    inputs: Dict[str, Union[str, List[str]]]
    multi_label: bool = False
    explanation: Optional[Dict[str, List[TokenAttributions]]] = None

    _SCORE_DEVIATION_ERROR: ClassVar[float] = 0.001

    @root_validator
    def validate_record(cls, values):
        """fastapi validator method"""
        prediction = values.get("prediction", None)
        multi_label = values.get("multi_label", False)

        cls._check_score_integrity(prediction, multi_label)
        return values

    @classmethod
    def _check_score_integrity(
        cls, prediction: TextClassificationAnnotation, multi_label: bool
    ):
        """
        Checks the score value integrity

        Parameters
        ----------
        prediction:
            The prediction annotation
        multi_label:
            If multi label

        """
        if prediction and not multi_label:
            assert sum([label.score for label in prediction.labels]) <= (
                1.0 + cls._SCORE_DEVIATION_ERROR
            ), f"Wrong score distributions: {prediction.labels}"

    @classmethod
    def task(cls) -> TaskType:
        """The task type"""
        return TaskType.text_classification

    @property
    def predicted(self) -> Optional[PredictionStatus]:
        if self.predicted_as and self.annotated_as:
            return (
                PredictionStatus.OK
                if set(self.predicted_as) == set(self.annotated_as)
                else PredictionStatus.KO
            )
        return None

    @property
    def words(self) -> str:
        sentences = []
        for v in self.inputs.values():
            if isinstance(v, list):
                sentences.extend(v)
            else:
                sentences.append(v)
        return "\n".join(sentences)

    @property
    def predicted_as(self) -> List[str]:
        return self._labels_from_annotation(
            self.prediction, multi_label=self.multi_label
        )

    @property
    def annotated_as(self) -> List[str]:
        return self._labels_from_annotation(
            self.annotation, multi_label=self.multi_label
        )

    @property
    def scores(self) -> List[float]:
        """Values of prediction scores"""
        if not self.prediction:
            return []
        return (
            [label.score for label in self.prediction.labels]
            if self.multi_label
            else [
                prediction_class.score
                for prediction_class in [
                    self._max_class_prediction(
                        self.prediction, multi_label=self.multi_label
                    )
                ]
                if prediction_class
            ]
        )

    @validator("inputs")
    def validate_inputs(cls, text: Dict[str, Any]):
        """Applies validation over input text"""
        assert len(text) > 0, "No inputs provided"

        for t in text.values():
            assert t is not None, "Cannot include None fields"

        return text

    @validator("inputs")
    def flatten_text(cls, text: Dict[str, Any]):
        """Normalizes input text to dict of strings"""
        flat_dict = flatten_dict(text)
        return flat_dict

    @classmethod
    def _labels_from_annotation(
        cls, annotation: TextClassificationAnnotation, multi_label: bool
    ) -> Union[List[str], List[int]]:
        """
        Extracts labels values from annotation

        Parameters
        ----------
        annotation:
            The annotation
        multi_label
            Enable/Disable multi label model

        Returns
        -------
            Label values for a given annotation

        """
        if not annotation:
            return []

        if multi_label:
            return [
                label.class_label for label in annotation.labels if label.score > 0.5
            ]

        class_prediction = cls._max_class_prediction(
            annotation, multi_label=multi_label
        )
        if class_prediction is None:
            return []

        return [class_prediction.class_label]

    @staticmethod
    def _max_class_prediction(
        p: TextClassificationAnnotation, multi_label: bool
    ) -> Optional[ClassPrediction]:
        """
        Gets the max class prediction for annotation

        Parameters
        ----------
        p:
            The annotation
        multi_label:
            Enable/Disable multi_label mode

        Returns
        -------

            The max class prediction in terms of prediction score if
            prediction has labels and no multi label is enabled. None, otherwise
        """
        if multi_label or p is None or not p.labels:
            return None
        return p.labels[0]

    class Config:
        allow_population_by_field_name = True


class TextClassificationRecord(CreationTextClassificationRecord):
    """
    The main text classification task record

    Attributes:
    -----------

    last_updated: datetime
        Last record update (read only)
    predicted: Optional[PredictionStatus]
        The record prediction status. Optional
    """

    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")


class TextClassificationBulkData(UpdateDatasetRequest):
    """
    API bulk data for text classification

    Attributes:
    -----------

    records: List[CreationTextClassificationRecord]
        The text classification record list

    """

    records: List[CreationTextClassificationRecord]


class TextClassificationQuery(BaseModel):
    """
    API Filters for text classification

    Attributes:
    -----------
    ids: Optional[List[Union[str, int]]]
        Record ids list

    query_text: str
        Text query over inputs
    metadata: Optional[Dict[str, Union[str, List[str]]]]
        Text query over metadata fields. Default=None

    predicted_as: List[str]
        List of predicted terms
    annotated_as: List[str]
        List of annotated terms
    annotated_by: List[str]
        List of annotation agents
    predicted_by: List[str]
        List of predicted agents
    status: List[TaskStatus]
        List of task status
    predicted: Optional[PredictionStatus]
        The task prediction status

    """

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

    class Config:
        allow_population_by_field_name = True


class TextClassificationSearchRequest(BaseModel):
    """
    API SearchRequest request

    Attributes:
    -----------

    query: TextClassificationQuery
        The search query configuration

    sort:
        The sort order list
    """

    query: TextClassificationQuery = Field(default_factory=TextClassificationQuery)
    sort: List[SortableField] = Field(default_factory=list)


class TextClassificationSearchAggregations(BaseSearchResultsAggregations):
    pass


class TextClassificationSearchResults(
    BaseSearchResults[TextClassificationRecord, TextClassificationSearchAggregations]
):
    pass
