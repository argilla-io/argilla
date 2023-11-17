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

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

import numpy as np

from argilla.client.feedback.metrics.base import AnnotatorMetricBase, AnnotatorMetricResult, MetricBase
from argilla.client.feedback.metrics.utils import (
    get_responses_and_suggestions_per_user,
    get_unified_responses_and_suggestions,
    is_multiclass,
    map_str_to_int,
)
from argilla.client.feedback.schemas import (
    LabelQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset


class AnnotatorMetric(MetricBase):
    """Main class to compute annotator metrics.

    Example:
        >>> import argilla as rg
        >>> from argilla.client.feedback.metrics import AnnotatorMetric
        >>> metric = AnnotatorMetric(dataset=dataset, question_name=question)
        >>> metrics_report = metric.compute("accuracy")

    """

    def __init__(self, dataset: "FeedbackDataset", question_name: str) -> None:
        self._metrics_per_question = METRICS_PER_QUESTION
        super().__init__(dataset, question_name)

    def compute(self, metric_names: Union[str, List[str]], **kwargs) -> Dict[str, List[AnnotatorMetricResult]]:
        """Computes the annotator metrics for the given question.

        Args:
            metric_names: name or list of names for the metrics to compute. i.e. `accuracy`
            kwargs: additional arguments to pass to the metric.

        Raises:
            ValueError: If the metric name is not supported for the given question.

        Returns:
            metrics: dict with the metrics computed for each annotator, where the
                key corresponds to the user id and the values are a list with the
                metric results.
        """
        metric_names = self._check_metrics(metric_names)
        metric_classes = self._get_metric_classes(metric_names)

        responses_per_user, suggestions = get_responses_and_suggestions_per_user(self._dataset, self._question_name)

        metrics = defaultdict(list)
        for user_id, responses in responses_per_user.items():
            for metric_name, metric_cls in metric_classes:
                metric = metric_cls(responses=responses, suggestions=suggestions)
                result = metric.compute(**kwargs)
                metrics[user_id].append(AnnotatorMetricResult(metric_name=metric_name, result=result))

        return dict(metrics)


class UnifiedAnnotationMetric(AnnotatorMetric):
    """Main class to compute metrics for a unified dataset.

    Example:
        >>> import argilla as rg
        >>> from argilla.client.feedback.metrics import UnifiedAnnotatorMetric
        >>> metric = UnifiedAnnotatorMetric(dataset=dataset, question_name=question)
        >>> metrics_report = metric.compute("accuracy")
    """

    def __init__(self, dataset: "FeedbackDataset", question_name: str) -> None:
        self._metrics_per_question = METRICS_PER_QUESTION_UNIFIED
        super().__init__(dataset, question_name)

    def compute(
        self, metric_names: Union[str, List[str]], **kwargs
    ) -> Union[AnnotatorMetricResult, List[AnnotatorMetricResult]]:
        """Computes the unified annotation metrics for the given question.

        Args:
            metric_names: name or list of names for the metrics to compute. i.e. `accuracy`
            kwargs: additional arguments to pass to the metric.

        Raises:
            ValueError: If the metric name is not supported for the given question.

        Returns:
            metrics: List of annotator metrics results if more than one metric is computed, or the result
                container if only one metric is computed.
        """
        metric_names = self._check_metrics(metric_names)
        metric_classes = self._get_metric_classes(metric_names)

        unified_responses, suggestions = get_unified_responses_and_suggestions(self._dataset, self._question_name)
        metrics = []
        for metric_name, metric_cls in metric_classes:
            metric = metric_cls(responses=unified_responses, suggestions=suggestions)
            result = metric.compute(**kwargs)
            metrics.append(AnnotatorMetricResult(metric_name=metric_name, result=result))

        if len(metric_names) == 1:
            return metrics[0]

        return metrics


class AccuracyMetric(AnnotatorMetricBase):
    """Accuracy score.

    Which proportion of the responses are equal to the suggestions offered.

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html#sklearn.metrics.accuracy_score

    In multilabel classification, this function computes subset accuracy: the set of labels predicted for a
    sample must exactly match the corresponding set of labels in y_true
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions, **kwargs):
        from sklearn.metrics import accuracy_score

        return accuracy_score(responses, suggestions, **kwargs)


class PrecisionMetric(AnnotatorMetricBase):
    """Compute the precision: tp / (tp + fp)

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html#sklearn.metrics.precision_score

    In case of multiclass data, calculate metrics for each label, and find their unweighted mean.
    This does not take label imbalance into account.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions, **kwargs):
        from sklearn.metrics import precision_score

        if is_multiclass(responses) or is_multiclass(suggestions):
            if not kwargs.get("average"):
                kwargs.update({"average": "macro"})
        return precision_score(responses, suggestions, **kwargs)


class RecallMetric(AnnotatorMetricBase):
    """Compute the recall: tp / (tp + fn)

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html#sklearn.metrics.recall_score

    In case of multiclass data, calculate metrics for each label, and find their unweighted mean.
    This does not take label imbalance into account.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions, **kwargs):
        from sklearn.metrics import recall_score

        if is_multiclass(responses) or is_multiclass(suggestions):
            if not kwargs.get("average"):
                kwargs.update({"average": "macro"})
        return recall_score(responses, suggestions, **kwargs)


class F1ScoreMetric(AnnotatorMetricBase):
    """F1 score: 2 * (precision * recall) / (precision + recall)

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html#sklearn.metrics.f1_score

    In case of multiclass data, calculate metrics for each label, and find their unweighted mean.
    This does not take label imbalance into account.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions, **kwargs):
        from sklearn.metrics import f1_score

        if is_multiclass(responses) or is_multiclass(suggestions):
            if not kwargs.get("average"):
                kwargs.update({"average": "macro"})
        return f1_score(responses, suggestions, **kwargs)


class ConfusionMatrixMetric(AnnotatorMetricBase):
    """Compute confusion matrix to evaluate the accuracy of an annotator.

    In case of multiclass classification, this function returns a confusion matrix class-wise.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions, **kwargs):
        import pandas as pd
        from sklearn.metrics import confusion_matrix

        unique_responses = sorted(np.unique(responses))
        unique_suggestions = sorted(np.unique(suggestions))
        labels = sorted(set(unique_responses).union(set(unique_suggestions)))
        result = confusion_matrix(responses, suggestions, labels=labels, **kwargs)
        return pd.DataFrame(result, index=labels, columns=labels)


class PearsonCorrelationCoefficientMetric(AnnotatorMetricBase):
    def _pre_process(self, responses, suggestions) -> Tuple[List[int], List[int]]:
        return map_str_to_int(responses), map_str_to_int(suggestions)

    @requires_dependencies("scipy")
    def _compute(self, responses, suggestions, **kwargs):
        import scipy.stats as stats

        return stats.pearsonr(responses, suggestions)[0]


class SpearmanCorrelationCoefficientMetric(AnnotatorMetricBase):
    @requires_dependencies("scipy")
    def _compute(self, responses, suggestions, **kwargs):
        import scipy.stats as stats

        return stats.spearmanr(responses, suggestions)[0]


class GLEUMetric(AnnotatorMetricBase):
    """
    Improvement of BLEU that takes into account the length of the response.

    BLEU (Bilingual Evaluation Understudy) is an algorithm for evaluating the quality of text
    which has been machine-translated from one natural language to another.
    The Google-BLEU is an improvement of BLEU that adresses some undesirable properties found on
    single sentences.

    https://huggingface.co/spaces/evaluate-metric/bleu
    https://huggingface.co/spaces/evaluate-metric/google_bleu
    """

    def _pre_process(self, responses, suggestions) -> Any:
        return responses, [[suggestion] for suggestion in suggestions]

    @requires_dependencies("evaluate")
    def _compute(self, responses: List[str], suggestions: List[str], **kwargs):
        import evaluate

        gleu = evaluate.load("google_bleu")
        return gleu.compute(predictions=responses, references=suggestions, **kwargs)["google_bleu"]


class ROUGEMetric(AnnotatorMetricBase):
    """
    From the evaluate library:

        ROUGE, or Recall-Oriented Understudy for Gisting Evaluation, is a set of metrics and a software package
        used for evaluating automatic summarization and machine translation software in natural language processing.
        The metrics compare an automatically produced summary or translation against a reference or a set of references
        (human-produced) summary or translation.
        Note that ROUGE is case insensitive, meaning that upper case letters are treated the same way as lower case letters.

    https://huggingface.co/spaces/evaluate-metric/rouge
    """

    @requires_dependencies("evaluate")
    def _compute(self, responses: List[str], suggestions: List[str], **kwargs):
        import evaluate

        rouge = evaluate.load("rouge")
        return rouge.compute(predictions=responses, references=suggestions, **kwargs)


# TODO(plaguss): Currently sklearn doesn't support any metrics for multiclass-multioutput
# like the ones we offer for MultiLabel by default. We can either
# restrict the type of MultiLabelQuestion so we can compute
# for either multilabel or multiclass, or we have to define those metrics ourselves (or a use
# a different library)
# The following metric may work for RankingQuestion if the data is preprocessed
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.somersd.html.
# Otherwise we have the same problem that appears with MultiLabelQuestion

METRICS_PER_QUESTION = {
    LabelQuestion: {
        "accuracy": AccuracyMetric,
        "f1-score": F1ScoreMetric,
        "precision": PrecisionMetric,
        "recall": RecallMetric,
        "confusion-matrix": ConfusionMatrixMetric,
        "pearson-r": PearsonCorrelationCoefficientMetric,
    },
    RatingQuestion: {
        "accuracy": AccuracyMetric,
        "f1-score": F1ScoreMetric,
        "precision": PrecisionMetric,
        "recall": RecallMetric,
        "confusion-matrix": ConfusionMatrixMetric,
        "spearman-r": SpearmanCorrelationCoefficientMetric,
    },
    TextQuestion: {
        "gleu": GLEUMetric,
        "rouge": ROUGEMetric,
    },
}


METRICS_PER_QUESTION_UNIFIED = {
    LabelQuestion: METRICS_PER_QUESTION[LabelQuestion],
    RatingQuestion: METRICS_PER_QUESTION[RatingQuestion],
}
