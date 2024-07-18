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

"""This module contains metrics to gather information related to inter-Annotator agreement."""

import warnings
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Union

from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.metrics.base import AgreementMetricResult, AnnotationTaskMetricBase, MetricBase
from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
)
from argilla.client.feedback.schemas.remote.shared import RemoteSchema

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.metrics.base import FormattedResponses
    from argilla.client.feedback.schemas.enums import ResponseStatusFilter
    from argilla.client.feedback.schemas.records import SortBy


try:
    from nltk.metrics.agreement import AnnotationTask as NLTKAnnotationTask
    from nltk.metrics.distance import binary_distance, interval_distance, masi_distance
except (ImportError, ModuleNotFoundError):
    warnings.warn("nltk is not installed, please install it to use the agreement metrics.")

    class NLTKAnnotationTask:
        def __init__(self, **kwargs):
            raise ModuleNotFoundError("nltk is not installed, please install it to use the agreement metrics.")

    binary_distance = None
    interval_distance = None
    masi_distance = None


def prepare_dataset_for_annotation_task(
    dataset: Union["FeedbackDataset", "RemoteFeedbackDataset"],
    question_name: str,
    field_name: Union[str, List[str]],
    filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
    sort_by: Optional[List["SortBy"]] = None,
    max_records: Optional[int] = None,
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
        field_name: Name of the fields related to the question we want to analyse the agreement.
        filter_by: A dict with key the field to filter by, and values the filters to apply.
            Can be one of: draft, pending, submitted, and discarded. If set to None,
            no filter will be applied. Defaults to None (no filter is applied).
        sort_by: A list of `SortBy` objects to sort your dataset by.
            Defaults to None (no filter is applied).
        max_records: The maximum number of records to use for training. Defaults to None.

    Returns:
        formatted_responses: The responses formatted as a list of tuples of (user_id, question_id, value).
    """
    question_type = type(dataset.question_by_name(question_name))
    # Check to assume the remote questions behave just like local ones
    if issubclass(question_type, RemoteSchema):
        question_type = type(dataset.question_by_name(question_name).to_local())

    supported_question_types = list(QUESTION_TO_DISTANCE.keys())
    if question_type not in supported_question_types:
        raise NotImplementedError(
            f"Question '{question_name}' is of type '{question_type}', the supported question types are: {supported_question_types}."
        )

    if filter_by:
        dataset = dataset.filter_by(**filter_by)
    if sort_by:
        dataset = dataset.sort_by(sort_by)
    if max_records:
        dataset = dataset.pull(max_records=max_records)

    hf_dataset = dataset.format_as("datasets")

    formatted_responses: FormattedResponses = []

    for row in hf_dataset:
        responses_ = row[question_name]
        question_text = (
            " ".join([row[field] for field in field_name]) if isinstance(field_name, list) else row[field_name]
        )
        for response in responses_:
            user_id = response["user_id"]
            if user_id is None:
                raise ValueError(
                    "Please push your dataset to argilla to have the user_id necessary for this computation."
                )

            value = response["value"]
            if value is None:
                continue
            # To avoid errors with the MASI distance function
            if isinstance(value, list):
                if len(value) == 0:
                    continue
            if question_type == RankingQuestion:
                value = tuple(value["rank"])
            elif question_type == MultiLabelQuestion:
                value = frozenset(value)

            formatted_responses.append((user_id, question_text, value))

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
    """Main class to compute agreement metrics.

    Example:
        >>> import argilla as rg
        >>> from argilla.client.feedback.metrics import AgreementMetric
        >>> metric = AgreementMetric(dataset=dataset, question_name=question, field_name=field, filter_by={"response_status": "submitted"})
        >>> metrics_report = metric.compute("alpha")

    """

    def __init__(
        self,
        dataset: FeedbackDataset,
        question_name: str,
        field_name: Union[str, List[str]],
        filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
        sort_by: Optional[List["SortBy"]] = None,
        max_records: Optional[int] = None,
    ) -> None:
        """Initialize a `AgreementMetric` object to compute agreement metrics.

        Args:
            dataset: FeedbackDataset to compute the metrics.
            question_name: Name of the question for which we want to analyse the agreement.
            field_name: Name of the fields related to the question we want to analyse the agreement.
            filter_by: A dict with key the field to filter by, and values the filters to apply.
                Can be one of: draft, pending, submitted, and discarded. If set to None,
                no filter will be applied. Defaults to None (no filter is applied).
            sort_by: A list of `SortBy` objects to sort your dataset by.
                Defaults to None (no filter is applied).
            max_records: The maximum number of records to use for training. Defaults to None.
        """
        self._metrics_per_question = METRICS_PER_QUESTION
        self._field_name = field_name
        super().__init__(dataset, question_name)
        self._filter_by = filter_by
        self._sort_by = sort_by
        self._max_records = max_records

    def compute(self, metric_names: Union[str, List[str]]) -> List[AgreementMetricResult]:
        """Computes the agreement metrics for the given question.

        Args:
            metric_names: name or list of names for the metrics to compute. i.e. `alpha`.
            kwargs: additional arguments to pass to the metric.

        Raises:
            ValueError: If the metric name is not supported for the given question.

        Returns:
            agreement_metrics: A list of `AgreementMetricResult` objects for the dataset.
        """
        metric_names = self._check_metrics(metric_names)
        metric_classes = self._get_metric_classes(metric_names)

        dataset = prepare_dataset_for_annotation_task(
            self._dataset,
            self._question_name,
            self._field_name,
            filter_by=self._filter_by,
            sort_by=self._sort_by,
            max_records=self._max_records,
        )

        distance_function = QUESTION_TO_DISTANCE[self._question_type]

        metrics = []
        for metric_name, metric_cls in metric_classes:
            metric = metric_cls(annotated_dataset=dataset, distance_function=distance_function)
            result = metric.compute()
            metrics.append(AgreementMetricResult(metric_name=metric_name, result=result, count=len(dataset)))

        if len(metric_names) == 1:
            return metrics[0]

        return metrics


class NLTKAnnotationTaskMetric(NLTKAnnotationTask, AnnotationTaskMetricBase):
    """Base class for metrics that use the nltk's AnnotationTask class.

    These metrics make use of a distance function to compute the distance between

    It is often the case that we don't want to treat two different
    labels as complete disagreement, and so the AnnotationTask constructor can also
    take a distance metric as a final argument. Distance metrics are functions that take two
    arguments, and return a value between 0.0 and 1.0 indicating the distance between them.

    By default, the following distance metrics are provided for each type of question:

        For LabelQuestion, binary_distance:

        >>> am.binary_distance("a", "b")
        1.0
        >>> am.binary_distance("a", "a")
        0.0

        For MultiLabelQuestion, masi_distance:

        >>> label_sets = [
        ...     [frozenset(["a", "b"]), frozenset(["b", "a"])],
        ...     [frozenset(["a"]), frozenset(["a", "b"])],
        ...     [frozenset(["c"]), frozenset(["a", "b"])],
        ... ]
        >>> for a, b in label_sets:
        ...     print((a,b), am.masi_distance(a,b))
        ...
        (frozenset({'a', 'b'}), frozenset({'a', 'b'})) 0.0
        (frozenset({'a'}), frozenset({'a', 'b'})) 0.665
        (frozenset({'c'}), frozenset({'a', 'b'})) 1.0

        For RatingQuestion, interval_distance:

        >>> for a, b in [(1, 1), (1, 2), (3,6)]:
        ...     print((a,b), am.interval_distance(a,b))
        ...
        (1, 1) 0
        (1, 2) 1
        (3, 6) 9

        For RankingQuestion, kendall_tau_dist:

        >>> for i, a in enumerate(itertools.permutations(values, len(values))):
        ...     for j, b in enumerate(itertools.permutations(values, len(values))):
        ...         if j >= i:
        ...             print((a, b), kendall_tau_dist(a,b))
        ...
        ((1, 2, 3), (1, 2, 3)) 0.0
        ((1, 2, 3), (1, 3, 2)) 0.3333333333333333
        ((1, 2, 3), (2, 1, 3)) 0.3333333333333333
        ((1, 2, 3), (2, 3, 1)) 0.6666666666666667
        ((1, 2, 3), (3, 1, 2)) 0.6666666666666667
        ((1, 2, 3), (3, 2, 1)) 1.0
        ((1, 3, 2), (1, 3, 2)) 0.0
        ...
    """

    def __init__(self, annotated_dataset: "FormattedResponses" = None, distance_function: Callable = None) -> None:
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

    See Also:
        - Take a look at this metric definition:
        https://en.wikipedia.org/wiki/Krippendorff%27s_alpha

        - We use the implementation from nltk:
        https://www.nltk.org/api/nltk.metrics.agreement.html#nltk.metrics.agreement.AnnotationTask.alpha
    """

    def _compute(self, dataset) -> float:
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
