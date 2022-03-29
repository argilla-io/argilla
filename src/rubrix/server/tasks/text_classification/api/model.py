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
from rubrix.server.commons.es_helpers import filters
from rubrix.server.commons.helpers import flatten_dict
from rubrix.server.datasets.model import DatasetDB, UpdateDatasetRequest
from rubrix.server.tasks.commons.api.model import (
    BaseAnnotation,
    BaseRecord,
    BaseSearchResults,
    BaseSearchResultsAggregations,
    PredictionStatus,
    QueryRange,
    ScoreRange,
    SortableField,
    TaskStatus,
    TaskType,
)
from rubrix.server.tasks.search.model import BaseSearchQuery


class UpdateLabelingRule(BaseModel):
    label: Optional[str] = Field(
        default=None, description="@Deprecated::The label associated with the rule."
    )
    labels: List[str] = Field(
        default_factory=list,
        description="For multi label problems, a list of labels. "
        "It will replace the `label` field",
    )
    description: Optional[str] = Field(
        None, description="A brief description of the rule"
    )

    @root_validator
    def initialize_labels(cls, values):
        label = values.get("label", None)
        labels = values.get("labels", [])

        if label:
            labels.append(label)
            values["labels"] = list(set(labels))

        assert len(labels) >= 1, f"No labels was provided in rule {values}"
        return values


class CreateLabelingRule(UpdateLabelingRule):
    """
    Data model for labeling rules creation

    Attributes:
    -----------

    query:
        The ES query of the rule

    label: str
        The label associated with the rule

    description:
        A brief description of the rule

    """

    query: str = Field(description="The es rule query")

    @validator("query")
    def strip_query(cls, query: str) -> str:
        """Remove blank spaces for query"""
        return query.strip()


class LabelingRule(CreateLabelingRule):
    """
    Adds read-only attributes to the labeling rule

    Attributes:
    -----------

    author:
        Who created the rule

    created_at:
        When was the rule created

    """

    author: str = Field(description="User who created the rule")
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Rule creation timestamp"
    )


class LabelingRuleMetricsSummary(BaseModel):
    """Metrics generated for a labeling rule"""

    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None
    correct: Optional[float] = None
    incorrect: Optional[float] = None
    precision: Optional[float] = None

    total_records: int
    annotated_records: int


class DatasetLabelingRulesMetricsSummary(BaseModel):
    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None

    total_records: int
    annotated_records: int


class TextClassificationDatasetDB(DatasetDB):
    """
    A dataset class specialized for text classification task

    Attributes:
    -----------

        rules:
            A list of dataset labeling rules
    """

    task: TaskType = Field(default=TaskType.text_classification, const=True)

    rules: List[LabelingRule] = Field(default_factory=list)


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
        annotation = values.get("annotation", None)
        status = values.get("status")
        multi_label = values.get("multi_label", False)

        cls._check_score_integrity(prediction, multi_label)
        cls._check_annotation_integrity(annotation, multi_label, status)

        return values

    @classmethod
    def _check_annotation_integrity(
        cls,
        annotation: TextClassificationAnnotation,
        multi_label: bool,
        status: TaskStatus,
    ):
        if status == TaskStatus.validated and not multi_label:
            assert (
                annotation and len(annotation.labels) > 0
            ), "Annotation must include some label for validated records"

        if not multi_label and annotation:
            assert (
                len(annotation.labels) == 1
            ), "Single label record must include only one annotation label"

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

    def all_text(self) -> str:
        sentences = []
        for v in self.inputs.values():
            if isinstance(v, list):
                sentences.extend(v)
            else:
                sentences.append(v)
        return "\n".join(sentences)

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


class TextClassificationRecordDB(CreationTextClassificationRecord):
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

    def extended_fields(self) -> Dict[str, Any]:
        words = self.all_text()
        return {
            **super().extended_fields(),
            "words": words,
            # This allow query by text:.... or text.exact:....
            # Once words is remove we can normalize at record level
            "text": words,
        }


class TextClassificationRecord(TextClassificationRecordDB):
    def extended_fields(self) -> Dict[str, Any]:
        return {}


class TextClassificationBulkData(UpdateDatasetRequest):
    """
    API bulk data for text classification

    Attributes:
    -----------

    records: List[CreationTextClassificationRecord]
        The text classification record list

    """

    records: List[CreationTextClassificationRecord]

    @validator("records")
    def check_multi_label_integrity(cls, records: List[TextClassificationRecord]):
        """Checks all records in batch have same multi-label configuration"""
        if records:
            multi_label = records[0].multi_label
            for record in records[1:]:
                assert (
                    multi_label == record.multi_label
                ), "All records must be single/multi labelled"
        return records


class TextClassificationQuery(BaseSearchQuery):
    """
    API Filters for text classification

    Attributes:
    -----------

    predicted_as: List[str]
        List of predicted terms

    annotated_as: List[str]
        List of annotated terms

    predicted: Optional[PredictionStatus]
        The task prediction status

    uncovered_by_rules:
        Only return records that are NOT covered by these rules.

    """

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)

    uncovered_by_rules: List[str] = Field(
        default_factory=list,
        description="List of rule queries that WILL NOT cover the resulting records",
    )


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
