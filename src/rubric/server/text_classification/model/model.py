from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator
from rubric.server.commons.models import (
    BaseAnnotation,
    BaseRecord,
    PredictionStatus,
    RecordTaskInfo,
    TaskType,
    flatten_dict,
)


class ClassPrediction(BaseModel):
    """
    Single class prediction

    Attributes:
    -----------

    class_label: Union[str, int]
        the predicted class

    confidence: float
        the predicted class confidence. For human-supervised annotations,
        this probability should be 1.0
    """

    class_label: Union[str, int] = Field(alias="class")
    confidence: float = 1.0

    # See <https://pydantic-docs.helpmanual.io/usage/model_config>
    class Config:
        allow_population_by_field_name = True

    @validator("confidence")
    def check_confidence_ranges(cls, confidence: float):
        """Checks confidence value ranges"""
        assert 0.0 <= confidence <= 1.0
        return confidence


class TextClassificationAnnotation(BaseAnnotation):
    """
    Annotation class for text classification tasks

    Attributes:
    -----------

    labels: List[LabelPrediction]
        list of annotated labels with confidence
    """

    labels: List[ClassPrediction]

    @validator("labels")
    def sort_labels(cls, labels: List[ClassPrediction]):
        """Sort provided labels by confidence"""
        return sorted(labels, key=lambda x: x.confidence, reverse=True)


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


_CONFIDENCE_DEVIATION_ERROR = 0.001


def check_confidences_integrity(
    prediction: TextClassificationAnnotation, multi_label: bool
):
    """
    Checks the confidence value integrity

    Parameters
    ----------
    prediction:
        The prediction annotation
    multi_label:
        If multi label

    """
    if prediction and not multi_label:
        assert sum([label.confidence for label in prediction.labels]) <= (
            1.0 + _CONFIDENCE_DEVIATION_ERROR
        ), f"Wrong confidence distributions: {prediction.labels}"


class TextClassificationTask(RecordTaskInfo[TextClassificationAnnotation]):
    """
    Task info for text classification

    Attributes:
    -----------
    multi_label: bool
        Enable text classification with multiple predicted/annotated labels.
        Default=False

    explanation: Dict[str, List[TokenAttributions]]
        Token attribution list explaining predicted classes per token input.
        The dictionary key must be aligned with provided record text

    """

    multi_label: bool = False
    explanation: Dict[str, List[TokenAttributions]] = None

    @root_validator
    def validate_record(cls, values):
        """fastapi validator method"""
        prediction = values.get("prediction", None)
        multi_label = values.get("multi_label", False)

        check_confidences_integrity(prediction, multi_label)
        return values

    @classmethod
    def task(cls) -> TaskType:
        """The task type"""
        return TaskType.text_classification

    @property
    def predicted(self) -> Optional[PredictionStatus]:
        if self.predicted_as and self.annotated_as:
            return (
                PredictionStatus.OK
                if self.predicted_as == self.annotated_as
                else PredictionStatus.KO
            )
        return None

    @property
    def predicted_as(self) -> List[str]:
        return labels_from_annotation(self.prediction, multi_label=self.multi_label)

    @property
    def annotated_as(self) -> List[str]:
        return labels_from_annotation(self.annotation, multi_label=self.multi_label)

    @property
    def confidences(self) -> List[float]:
        """Values of prediction confidences"""
        if not self.prediction:
            return []
        return (
            [label.confidence for label in self.prediction.labels]
            if self.multi_label
            else [
                max_class_prediction(
                    self.prediction, multi_label=self.multi_label
                ).confidence
            ]
        )

    def extended_fields(self) -> Dict[str, Any]:
        """Store confidences values for supporting by-confidence filters and aggregations"""
        return {"confidences": self.confidences}


def labels_from_annotation(
    annotation: TextClassificationAnnotation, multi_label: bool
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
            label.class_label for label in annotation.labels if label.confidence > 0.5
        ]

    class_prediction = max_class_prediction(annotation, multi_label=multi_label)
    if class_prediction is None:
        return []

    return [class_prediction.class_label]


def max_class_prediction(
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

        The max class prediction in terms of prediction confidence if
        prediction has labels and no multi label is enabled. None, otherwise
    """
    if multi_label or p is None or not p.labels:
        return None
    return p.labels[0]


class CreationTextClassificationRecord(BaseRecord, TextClassificationTask):
    """
    Dataset record for text classification task

    Attributes:
    -----------

    text: Dict[str, Any]
        The input data text
    """

    text: Dict[str, Any] = Field(alias="inputs")

    @validator("text")
    def validate_inputs(cls, text: Dict[str, Any]):
        """Applies validation over input text"""
        assert len(text) > 0, "No inputs provided"

        for t in text.values():
            assert t is not None, "Cannot include None fields"

        return text

    @validator("text")
    def flatten_inputs(cls, text: Dict[str, Any]):
        """Normalizes input text to dict of strings"""
        return flatten_dict(text)

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
