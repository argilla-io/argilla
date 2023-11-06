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

"""This module contains metrics to compare Annotator's suggestions vs responses. """

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Literal, Union

from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.schemas.types import AllowedQuestionTypes

import evaluate
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    multilabel_confusion_matrix,
    precision_score,
    recall_score,
)


class AnnotatorMetric:
    # This class should be in charge of computing the metrics for a given question,
    # but internally we should have a class hierarchy with the metrics implemented
    def __init__(self, dataset: FeedbackDataset, question_name: "AllowedQuestionTypes") -> None:
        self._dataset = dataset
        self._question_name = question_name
        question_type = self._dataset.question_by_name(question_name)
        self._allowed_metrics = METRICS_PER_QUESTION[question_type]

    def compute(self, metric_name: Union[str, List[str]], **kwargs) -> float:
        # Only one for the moment, otherwise return a dict or list?
        if metric not in self._allowed_metrics.keys():
            raise ValueError(f"Metric {metric} not allowed for question {self._question_name}")
        metric_cls = self._allowed_metrics[metric_name]

        # prepare data
        df = self._dataset.format_as("datasets").to_pandas()
        metric = metric_cls(responses=df[self._question_name], suggestions=df[f"{self._question_name}-suggestion"])
        # TODO(plaguss): check if the question has a suggestion field
        # TODO(plaguss): check all the metrics are available for the question type
        # TODO(plaguss): check the functions use the same parameters
        result = metric.compute(**kwargs)

        return AnnotatorMetricResult(metric_name=metric, result=result)


@dataclass
class AnnotatorMetricResult:
    metric_name: str
    result: float


class AnnotatorMetricBase(ABC):
    def __init__(self, responses=None, suggestions=None) -> None:
        self._responses = responses
        self._suggestions = suggestions

    def compute(self, **kwargs):
        result = self._compute(self._responses, self._suggestions, **kwargs)
        return self._post_process(result)

    def _post_process(self, result: Any) -> Any:
        """It should prepare the result to be returned to the user to be more informative.

        Args:
            result: _description_

        Returns:
            Any: _description_
        """
        return result

    @abstractmethod
    def _compute(self, responses, suggestions, **kwargs):
        pass


class AccuracyMetric(AnnotatorMetricBase):
    def _compute(self, responses, suggestions, **kwargs):
        return accuracy_score(responses, suggestions, **kwargs)


class F1ScoreMetric(AnnotatorMetricBase):
    def _compute(self, responses, suggestions, **kwargs):
        return f1_score(responses, suggestions, **kwargs)


class PrecisionMetric(AnnotatorMetricBase):
    def _compute(self, responses, suggestions, **kwargs):
        return precision_score(responses, suggestions, **kwargs)


class RecallMetric(AnnotatorMetricBase):
    def _compute(self, responses, suggestions, **kwargs):
        return recall_score(responses, suggestions, **kwargs)


class ConfusionMatrixMetric(AnnotatorMetricBase):
    def _compute(self, responses, suggestions, **kwargs):
        return confusion_matrix(responses, suggestions, **kwargs)


class MultiLabelConfusionMatrixMetric(AnnotatorMetricBase):
    def _compute(self, responses, suggestions, **kwargs):
        return multilabel_confusion_matrix(responses, suggestions, **kwargs)


class CorrelationCoefficientMetric(AnnotatorMetricBase):
    def _compute(self, responses, suggestions, kind: Literal["pearson", "spearman", "kendall"] = "spearman", **kwargs):
        return pd.DataFrame({"responses": responses, "suggestions": suggestions}).corr(method=kind)


class GLEUMetric(AnnotatorMetricBase):
    # https://huggingface.co/spaces/evaluate-metric/google_bleu
    def _compute(self, responses: List[str], suggestions: List[str], **kwargs):
        gleu = evaluate.load("google_bleu")
        # The data must be transformed here before being processed
        return gleu.compute(predictions=responses, references=[suggestions], **kwargs)

    def _post_process(self, result: Any) -> Any:
        return result["google_bleu"]


class ROUGEMetric(AnnotatorMetricBase):
    # https://huggingface.co/spaces/evaluate-metric/rouge
    def _compute(self, responses: List[str], suggestions: List[str], **kwargs):
        rouge = evaluate.load("rouge")
        return rouge.compute(predictions=responses, references=suggestions, **kwargs)


METRICS_PER_QUESTION = {
    LabelQuestion: {
        "accuracy": AccuracyMetric,
        "f1-score": F1ScoreMetric,
        "precision": PrecisionMetric,
        "recall": RecallMetric,
        "confusion-matrix": ConfusionMatrixMetric,
    },
    MultiLabelQuestion: {
        "accuracy": AccuracyMetric,
        "f1-score": F1ScoreMetric,
        "precision": PrecisionMetric,
        "recall": RecallMetric,
        "confusion-matrix": MultiLabelConfusionMatrixMetric,
    },
    RatingQuestion: {
        "accuracy": AccuracyMetric,
        "f1-score": F1ScoreMetric,
        "precision": PrecisionMetric,
        "recall": RecallMetric,
        "confusion-matrix": ConfusionMatrixMetric,
        "spearman-r": CorrelationCoefficientMetric,
    },
    RankingQuestion: {
        "accuracy": AccuracyMetric,
        "f1-score": F1ScoreMetric,
        "precision": PrecisionMetric,
        "recall": RecallMetric,
        "confusion-matrix": ConfusionMatrixMetric,
    },
    TextQuestion: {
        "GLEU": GLEUMetric,
        "ROUGE": ROUGEMetric,
    },
}
