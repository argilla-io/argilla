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

"""This module contains metrics for Suggestions Metric and Responses Metric."""

import random
import warnings
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.metrics.base import AnnotatorMetricBase, MetricBase, ModelMetricResult
from argilla.client.feedback.metrics.utils import (
    get_responses_and_suggestions_per_user,
    get_unified_responses_and_suggestions,
    is_multiclass,
    map_str_to_int,
)
from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.enums import ResponseStatusFilter
from argilla.client.feedback.schemas.records import SortBy
from argilla.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.metrics.base import Responses, Suggestions
    from argilla.client.feedback.schemas.enums import ResponseStatusFilter
    from argilla.client.feedback.schemas.records import SortBy


class AnnotatorMetric(MetricBase):
    """Main class to compute annotator metrics. Annotator metrics refers to the combination of Suggestions Metric and Responses Metric. They are both different from the Agreement Metric (i.e. Inter-Annotator Agreement) and they are utilized to compute metrics contrasting suggestions vs responses.

    Example:
        >>> import argilla as rg
        >>> from argilla.client.feedback.metrics import AnnotatorMetric
        >>> metric = AnnotatorMetric(dataset=dataset, question_name=question)
        >>> metrics_report = metric.compute("accuracy")

    """

    def __init__(
        self,
        dataset: "FeedbackDataset",
        question_name: str,
        filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
        sort_by: Optional[List["SortBy"]] = None,
        max_records: Optional[int] = None,
        responses_vs_suggestions: bool = True,
    ) -> None:
        """Initialize an `AnnotatorMetric` object to compute agreement metrics for both Suggestions Metric and Responses Metric.

        Args:
            dataset: FeedbackDataset to compute the metrics.
            question_name: Name of the question for which we want to analyse the agreement.
            filter_by: A dict with key the field to filter by, and values the filters to apply.
                Can be one of: draft, pending, submitted, and discarded. If set to None,
                no filter will be applied. Defaults to None (no filter is applied).
            sort_by: A list of `SortBy` objects to sort your dataset by.
                Defaults to None (no filter is applied).
            max_records: The maximum number of records to use for training. Defaults to None.
            responses_vs_suggestions: Whether to utilize Suggestions Metric (where the suggestions are the ground truths and the responses are compared against them) or Responses Metric (where the responses are the ground truths and the suggestions are compared against them). Defaults to True, i.e. Responses Metric.
        """
        self._metrics_per_question = METRICS_PER_QUESTION
        super().__init__(dataset, question_name, responses_vs_suggestions=responses_vs_suggestions)
        self._filter_by = filter_by
        self._sort_by = sort_by
        self._max_records = max_records

    def _check_responses_and_suggestions(
        self, responses_per_user: Dict[int, "Responses"], suggestions: "Suggestions"
    ) -> Tuple[Dict[int, "Responses"], "Suggestions"]:
        # Check for possible missing suggestions
        df_suggestions = pd.Series(suggestions)
        df_responses_per_user = pd.DataFrame(responses_per_user)
        df_responses_per_user = df_responses_per_user[df_suggestions.notna()]
        df_suggestions = df_suggestions[df_suggestions.notna()]
        total_responses = len(suggestions)

        responses_per_user = df_responses_per_user.to_dict(orient="list")
        suggestions = df_suggestions.to_list()

        if len(suggestions) == 0:
            raise ValueError("All the suggestions are None, the metric cannot be computed.")
        elif len(suggestions) < total_responses:
            warnings.warn("Some suggestions are None, the metric will be computed without them.")
        return responses_per_user, suggestions

    def compute(
        self, metric_names: Union[str, List[str]], show_progress: bool = True
    ) -> Dict[str, List[ModelMetricResult]]:
        """Computes the annotator metrics for the given question.

        Args:
            metric_names: name or list of names for the metrics to compute. i.e. `accuracy`

        Raises:
            ValueError: If the metric name is not supported for the given question.

        Returns:
            metrics: dict with the metrics computed for each annotator, where the
                key corresponds to the user id and the values are a list with the
                metric results.
        """
        metric_names = self._check_metrics(metric_names)
        metric_classes = self._get_metric_classes(metric_names)

        responses_and_suggestions_per_user = get_responses_and_suggestions_per_user(
            self._dataset,
            self._question_name,
            filter_by=self._filter_by,
            sort_by=self._sort_by,
            max_records=self._max_records,
        )
        metrics = defaultdict(list)
        for user_id, resp_and_suggest in responses_and_suggestions_per_user.items():
            responses = resp_and_suggest["responses"]
            suggestions = resp_and_suggest["suggestions"]
            as_responses, as_suggestions = self._prepare_responses_and_suggestions(responses, suggestions)
            for metric_name, metric_cls in metric_classes:
                metric = metric_cls(responses=as_responses, suggestions=as_suggestions)
                result = metric.compute()
                metrics[user_id].append(ModelMetricResult(metric_name=metric_name, result=result, count=len(responses)))

        return dict(metrics)


class ModelMetric(AnnotatorMetric):
    """Where suggestions are the ground truths and the responses are compared against them."""

    def __init__(
        self,
        dataset: FeedbackDataset,
        question_name: str,
        filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
        sort_by: Optional[List["SortBy"]] = None,
        max_records: Optional[int] = None,
    ) -> None:
        super().__init__(
            dataset,
            question_name,
            filter_by=filter_by,
            sort_by=sort_by,
            max_records=max_records,
            responses_vs_suggestions=True,
        )


class UnifiedAnnotatorMetric(AnnotatorMetric):
    """Main class to compute metrics for a unified dataset.

    Example:
        >>> import argilla as rg
        >>> from argilla.client.feedback.metrics import UnifiedAnnotatorMetric
        >>> metric = UnifiedAnnotatorMetric(dataset=dataset, question_name=question)
        >>> metrics_report = metric.compute("accuracy")
    """

    def __init__(
        self,
        dataset: "FeedbackDataset",
        question_name: str,
        strategy_name: str = "majority",
        filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
        sort_by: Optional[List["SortBy"]] = None,
        max_records: Optional[int] = None,
        responses_vs_suggestions: bool = True,
    ) -> None:
        self._metrics_per_question = METRICS_PER_QUESTION_UNIFIED
        super().__init__(dataset, question_name, responses_vs_suggestions=responses_vs_suggestions)
        self._filter_by = filter_by
        self._sort_by = sort_by
        self._max_records = max_records
        self._strategy_name = strategy_name

    def _check_responses_and_suggestions(
        self, unified_responses: "Responses", suggestions: "Suggestions"
    ) -> Tuple["Responses", "Suggestions"]:
        # Check for possible missing suggestions
        df_suggestions = pd.Series(suggestions)
        df_responses = pd.Series(unified_responses)
        df_responses = df_responses[df_suggestions.notna()]
        df_suggestions = df_suggestions[df_suggestions.notna()]
        total_responses = len(suggestions)

        unified_responses = df_responses.to_list()
        suggestions = df_suggestions.to_list()

        if len(suggestions) == 0:
            raise ValueError("All the suggestions are None, the metric cannot be computed.")
        elif len(suggestions) < total_responses:
            warnings.warn("Some suggestions are None, the metric will be computed without them.")
        return unified_responses, suggestions

    def compute(self, metric_names: Union[str, List[str]]) -> Union[ModelMetricResult, List[ModelMetricResult]]:
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

        unified_responses, suggestions = get_unified_responses_and_suggestions(
            self._dataset,
            self._question_name,
            strategy_name=self._strategy_name,
            filter_by=self._filter_by,
            sort_by=self._sort_by,
            max_records=self._max_records,
        )
        self._check_responses_and_suggestions(unified_responses, suggestions)

        as_unified_responses, as_suggestions = self._prepare_responses_and_suggestions(unified_responses, suggestions)
        metrics = []
        for metric_name, metric_cls in metric_classes:
            metric = metric_cls(responses=as_unified_responses, suggestions=as_suggestions)
            result = metric.compute()
            metrics.append(ModelMetricResult(metric_name=metric_name, result=result, count=len(unified_responses)))

        if len(metric_names) == 1:
            return metrics[0]

        return metrics


class UnifiedModelMetric(UnifiedAnnotatorMetric):
    """"""

    def __init__(
        self,
        dataset: "FeedbackDataset",
        question_name: str,
        filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
        sort_by: Optional[List["SortBy"]] = None,
        max_records: Optional[int] = None,
    ) -> None:
        super().__init__(
            dataset,
            question_name,
            filter_by=filter_by,
            sort_by=sort_by,
            max_records=max_records,
            responses_vs_suggestions=True,
        )


class AccuracyMetric(AnnotatorMetricBase):
    """Accuracy score.

    Which proportion of the responses are equal to the suggestions offered.

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html#sklearn.metrics.accuracy_score

    In multilabel classification, this function computes subset accuracy: the set of labels predicted for a
    sample must exactly match the corresponding set of labels in y_true
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import accuracy_score

        return accuracy_score(y_true=responses, y_pred=suggestions)


class PrecisionMetric(AnnotatorMetricBase):
    """Compute the precision: tp / (tp + fp)

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html#sklearn.metrics.precision_score

    In case of multiclass data, calculate metrics for each label, and find their unweighted mean.
    This does not take label imbalance into account.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import precision_score

        if is_multiclass(responses) or is_multiclass(suggestions):
            kwargs = {"average": "macro"}
        else:
            kwargs = {"average": "binary", "pos_label": random.choice(np.unique(responses))}
        return precision_score(y_true=responses, y_pred=suggestions, **kwargs)


class RecallMetric(AnnotatorMetricBase):
    """Compute the recall: tp / (tp + fn)

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html#sklearn.metrics.recall_score

    In case of multiclass data, calculate metrics for each label, and find their unweighted mean.
    This does not take label imbalance into account.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import recall_score

        if is_multiclass(responses) or is_multiclass(suggestions):
            kwargs = {"average": "macro"}
        else:
            kwargs = {"average": "binary", "pos_label": random.choice(np.unique(responses))}
        return recall_score(y_true=responses, y_pred=suggestions, **kwargs)


class F1ScoreMetric(AnnotatorMetricBase):
    """F1 score: 2 * (precision * recall) / (precision + recall)

    We use the implementation in:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html#sklearn.metrics.f1_score

    In case of multiclass data, calculate metrics for each label, and find their unweighted mean.
    This does not take label imbalance into account.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import f1_score

        if is_multiclass(responses) or is_multiclass(suggestions):
            kwargs = {"average": "macro"}
        else:
            kwargs = {"average": "binary", "pos_label": random.choice(np.unique(responses))}

        return f1_score(responses, suggestions, **kwargs)


class MultiLabelMetrics(AnnotatorMetricBase):
    """Parent class for MultiLabel based metrics. It binarizes the data to compute the metrics."""

    @requires_dependencies("scikit-learn")
    def _pre_process(self, responses, suggestions) -> Any:
        from sklearn.preprocessing import MultiLabelBinarizer

        classes = sorted(set(responses).union(set(suggestions)))
        # Keep the binarizer to access the classes later
        self._mlb = MultiLabelBinarizer()
        self._mlb.fit(classes)
        responses = self._mlb.transform(responses)
        suggestions = self._mlb.transform(suggestions)
        return responses, suggestions

    def _compute(self, responses, suggestions):
        # Child classes are in charge of the implementation
        pass


class MultiLabelAccuracyMetric(MultiLabelMetrics):
    """Computes the accuracy on the binarized data for multilabel classification.

    See Also:
        https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MultiLabelBinarizer.html
        `AccuracyMetric`
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import accuracy_score

        return accuracy_score(y_true=responses, y_pred=suggestions)


class MultiLabelPrecisionMetric(MultiLabelMetrics):
    """Computes the precision on the binarized data for multilabel classification.

    See Also:
        https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MultiLabelBinarizer.html
        `PrecisionMetric`
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import precision_score

        return precision_score(y_true=responses, y_pred=suggestions, average="macro")


class MultiLabelRecallMetric(MultiLabelMetrics):
    """Computes the recall on the binarized data for multilabel classification.

    See Also:
        https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MultiLabelBinarizer.html
        `RecallMetric`
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import recall_score

        return recall_score(y_true=responses, y_pred=suggestions, average="macro")


class MultiLabelF1ScoreMetric(MultiLabelMetrics):
    """Computes the f1-score on the binarized data for multilabel classification.

    See Also:
        https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MultiLabelBinarizer.html
        `F1ScoreMetric`
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        from sklearn.metrics import f1_score

        return f1_score(y_true=responses, y_pred=suggestions, average="macro")


class ConfusionMatrixMetric(AnnotatorMetricBase):
    """Compute confusion matrix to evaluate the accuracy of an annotator.

    In case of multiclass classification, this function returns a confusion matrix class-wise.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        import pandas as pd
        from sklearn.metrics import confusion_matrix

        unique_responses = sorted(np.unique(responses))
        unique_suggestions = sorted(np.unique(suggestions))
        labels = sorted(set(unique_responses).union(set(unique_suggestions)))
        labels_index = [f"responses_{label}" for label in labels]
        labels_columns = [f"suggestions_{label}" for label in labels]
        result = confusion_matrix(y_true=responses, y_pred=suggestions, labels=labels)
        return pd.DataFrame(result, index=labels_index, columns=labels_columns)


class MultiLabelConfusionMatrixMetric(MultiLabelMetrics):
    """Compute confusion matrix to evaluate the accuracy of an annotator.

    The data is binarized, so we will return a dict with the confusion matrix for each class.
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses, suggestions):
        import pandas as pd
        from sklearn.metrics import multilabel_confusion_matrix

        unique_responses = sorted(np.unique(responses))
        unique_suggestions = sorted(np.unique(suggestions))
        labels = sorted(set(unique_responses).union(set(unique_suggestions)))
        matrices = multilabel_confusion_matrix(y_true=responses, y_pred=suggestions, labels=labels)
        report = {}
        for class_, matrix in zip(self._mlb.classes_, matrices):
            labels_index = [f"responses_{class_}_{i}" for i in ["true", "false"]]
            labels_columns = [f"suggestions_{class_}_{i}" for i in ["true", "false"]]
            report[class_] = pd.DataFrame(matrix, index=labels_index, columns=labels_columns)
        return report


class PearsonCorrelationCoefficientMetric(AnnotatorMetricBase):
    def _pre_process(self, responses, suggestions) -> Tuple[List[int], List[int]]:
        return map_str_to_int(responses), map_str_to_int(suggestions)

    @requires_dependencies("scipy")
    def _compute(self, responses, suggestions):
        import scipy.stats as stats

        return stats.pearsonr(x=suggestions, y=responses)[0]


class SpearmanCorrelationCoefficientMetric(AnnotatorMetricBase):
    @requires_dependencies("scipy")
    def _compute(self, responses, suggestions):
        import scipy.stats as stats

        return stats.spearmanr(a=suggestions, b=responses)[0]


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
    def _compute(self, responses: List[str], suggestions: List[str]):
        import evaluate

        gleu = evaluate.load("google_bleu")
        return gleu.compute(predictions=responses, references=suggestions)["google_bleu"]  # test is symmetrical


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
    def _compute(self, responses: List[str], suggestions: List[str]):
        import evaluate

        rouge = evaluate.load("rouge")
        return rouge.compute(predictions=responses, references=suggestions)  # test is symmetrical


class NDCGMetric(AnnotatorMetricBase):
    """Compute Normalized Discounted Cumulative Gain.

    From the Wikipedia page for Discounted Cumulative Gain:

    “Discounted cumulative gain (DCG) is a measure of ranking quality. In information retrieval,
    it is often used to measure effectiveness of web search engine algorithms or related applications.
    Using a graded relevance scale of documents in a search-engine result set, DCG measures the usefulness,
    or gain, of a document based on its position in the result list. The gain is accumulated from the
    top of the result list to the bottom, with the gain of each result discounted at lower ranks”

    See Also:
        https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
        https://en.wikipedia.org/wiki/Discounted_cumulative_gain
    """

    @requires_dependencies("scikit-learn")
    def _compute(self, responses: List[str], suggestions: List[str]):
        from sklearn.metrics import ndcg_score

        return ndcg_score(y_true=responses, y_score=suggestions)


METRICS_PER_QUESTION = {
    LabelQuestion: {
        "accuracy": AccuracyMetric,
        "f1-score": F1ScoreMetric,
        "precision": PrecisionMetric,
        "recall": RecallMetric,
        "confusion-matrix": ConfusionMatrixMetric,
        "pearson-r": PearsonCorrelationCoefficientMetric,
    },
    MultiLabelQuestion: {
        "accuracy": MultiLabelAccuracyMetric,
        "f1-score": MultiLabelF1ScoreMetric,
        "precision": MultiLabelPrecisionMetric,
        "recall": MultiLabelRecallMetric,
        "confusion-matrix": MultiLabelConfusionMatrixMetric,
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
    RankingQuestion: {
        "ndcg-score": NDCGMetric,
    },
}


METRICS_PER_QUESTION_UNIFIED = {
    LabelQuestion: METRICS_PER_QUESTION[LabelQuestion],
    MultiLabelQuestion: METRICS_PER_QUESTION[MultiLabelQuestion],
    RatingQuestion: METRICS_PER_QUESTION[RatingQuestion],
    RankingQuestion: METRICS_PER_QUESTION[RankingQuestion],
}
