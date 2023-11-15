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

"""This module contains metrics to gather information related to inter-Annotator agreement. """

from typing import TYPE_CHECKING, List, Union

from nltk.metrics.agreement import AnnotationTask as NLTKAnnotationTask
from nltk.metrics.distance import binary_distance, interval_distance, jaro_similarity, masi_distance

from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.metrics.base import AgreementMetricResult, AnnotationTaskMetricBase, MetricBase
from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
)
from argilla.client.feedback.schemas.enums import ResponseStatusFilter
from argilla.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.metrics.base import FormattedResponses


def prepare_dataset_for_annotation_task(
    dataset: Union["FeedbackDataset", "RemoteFeedbackDataset"], question_name: str
) -> "FormattedResponses":
    """Helper function to prepare the dataset for the nltk's AnnotationTask.

    The AnnotationTask class from nltk expects the data to be formatted as a list
    of tuples, each containing the annotator id, the task id and the label.

    The AnnotationTask is supposed to deal with sets and hashable objects, but
    there are errors transforming the data to sets and using the MASI distance function.
    For the moment what we do with those type of questions is create a string
    with all the values, and use the edit distance function.

    Note:
        We could potentially extend the functionality to a more than a question name. The
        requirement would be that all the questions are of the same type, as that would
        determine the type of distance function to use.

    Args:
        dataset: FeedbackDataset to compute the metrics.
        question_name: Name of the question for which we want to analyse the agreement.

    Returns:
        formatted_responses: The responses formatted as a list of tuples of (user_id, question_id, value).
    """
    question_type = type(dataset.question_by_name(question_name))
    supported_question_types = list(QUESTION_TO_DISTANCE.keys())
    if question_type not in supported_question_types:
        raise NotImplementedError(
            f"Question '{question_name}' is of type '{question_type}', the supported question types are: {supported_question_types}."
        )

    dataset = dataset.filter_by(response_status=ResponseStatusFilter.submitted.value)

    hf_dataset = dataset.format_as("datasets")

    formatted_responses: FormattedResponses = []

    for responses_ in hf_dataset[question_name]:
        for response in responses_:
            # We do this check here because local datasets don't implement the filter_by method.
            if response["status"] != ResponseStatusFilter.submitted.value:
                continue
            user_id = response["user_id"]

            if user_id is None:
                raise ValueError(
                    "Please push your dataset to argilla to have the user_id necessary for this computation."
                )

            value = response["value"]
            if question_type == RankingQuestion:
                value = tuple(value["rank"])
            elif question_type == MultiLabelQuestion:
                value = frozenset(value)

            formatted_responses.append((user_id, question_name, value))

    return formatted_responses


def kendall_tau_dist(x: List[int], y: List[int]) -> float:
    r"""Kendall tau distance.

    https://en.wikipedia.org/wiki/Kendall_tau_distance

    Args:
        x: Values of the first annotation.
        y: Values of the first annotation.

    Returns:
        distance: Kendall tau distance.

    Example:
        >>> import itertools
        >>> values = (1, 2, 3)
        >>> for i, a in enumerate(itertools.permutations(values, len(values))):
        ...     for j, b in enumerate(itertools.permutations(values, len(values))):
        ...             if j >= i:
        ...                     print((a, b), kendall_tau_dist(a,b))
        ...
        ((1, 2, 3), (1, 2, 3)) 0.0
        ((1, 2, 3), (1, 3, 2)) 0.3333333333333333
        ((1, 2, 3), (2, 1, 3)) 0.3333333333333333
        ((1, 2, 3), (2, 3, 1)) 0.6666666666666667
        ((1, 2, 3), (3, 1, 2)) 0.6666666666666667
        ((1, 2, 3), (3, 2, 1)) 1.0
        ...
    """
    from scipy.stats import kendalltau

    coef, _ = kendalltau(x, y)
    return 0.5 * (1 - coef)


QUESTION_TO_DISTANCE = {
    LabelQuestion: binary_distance,
    MultiLabelQuestion: masi_distance,
    RatingQuestion: interval_distance,
    RankingQuestion: kendall_tau_dist,
}


class AgreementMetric(MetricBase):
    def __init__(self, dataset: FeedbackDataset, question_name: str) -> None:
        self._metrics_per_question = METRICS_PER_QUESTION
        super().__init__(dataset, question_name)

    def compute(self, metric_names: Union[str, List[str]], **kwargs) -> List[AgreementMetricResult]:
        """Computes the agreement metrics for the given question.

        Args:
            metric_names: name or list of names for the metrics to compute. i.e. `alpha`.
            kwargs: additional arguments to pass to the metric.

        Raises:
            ValueError: If the metric name is not supported for the given question.

        Returns:
            agreement_metrics: A list of `AgreementMetricResult` objects for the dataset.
        """
        if isinstance(metric_names, str):
            metric_names = [metric_names]

        if any([metric not in self._allowed_metrics for metric in metric_names]):
            raise ValueError(
                f"Metrics allowed for question {self._question_name}: {list(self._allowed_metrics.keys())}"
            )

        metric_classes = [(metric_name, self._allowed_metrics[metric_name]) for metric_name in metric_names]

        dataset = prepare_dataset_for_annotation_task(self._dataset, self._question_name)

        distance_function = kwargs.get("distance_function")
        if not distance_function:
            distance_function = QUESTION_TO_DISTANCE[self._question_type]

        metrics = []
        for metric_name, metric_cls in metric_classes:
            metric = metric_cls(annotated_dataset=dataset, distance_function=distance_function)
            result = metric.compute(**kwargs)
            metrics.append(AgreementMetricResult(metric_name=metric_name, result=result))

        return metrics


class NLTKAnnotationTaskMetric(NLTKAnnotationTask, AnnotationTaskMetricBase):
    """Base class for metrics that use the nltk's AnnotationTask class."""

    def __init__(self, annotated_dataset=None, distance_function=None) -> None:
        AnnotationTaskMetricBase.__init__(
            self, annotated_dataset=annotated_dataset, distance_function=distance_function
        )
        super().__init__(data=annotated_dataset, distance=distance_function)


class KrippendorfAlpha(NLTKAnnotationTaskMetric):
    """Krippendorf's alpha agreement metric.

    Is a statistical measure of the inter-annotator agreement achieved when coding a set
    of units of analysis.

    To interpret the results from this metric, we refer the reader to the wikipedia entry.
    The common consensus dictates that a value of alpha >= 0.8 indicates a reliable annotation,
    a value >= 0.667 can only guarantee tentative conclusions, while lower values suggest an
    unreliable annotation.

    Notes:
        - Take a look at this metric definition:
        https://en.wikipedia.org/wiki/Krippendorff%27s_alpha
        - We use the implementation from nltk:
        https://www.nltk.org/api/nltk.metrics.agreement.html#nltk.metrics.agreement.AnnotationTask.alpha
    """

    def _compute(self, dataset, **kwargs) -> float:
        return self.alpha()


METRICS_PER_QUESTION = {
    LabelQuestion: {
        "alpha": KrippendorfAlpha,
    },
    MultiLabelQuestion: {
        "alpha": KrippendorfAlpha,
    },
    RatingQuestion: {
        "alpha": KrippendorfAlpha,
    },
    RankingQuestion: {
        "alpha": KrippendorfAlpha,
    },
}
