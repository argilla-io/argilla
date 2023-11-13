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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Hashable, List, Tuple, Union

from nltk.metrics.agreement import AnnotationTask as NLTKAnnotationTask
from nltk.metrics.distance import binary_distance, edit_distance, interval_distance
from pydantic import BaseModel

from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.enums import ResponseStatusFilter

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset


# Expected format for the nltk's AnnotationTask
FormattedResponses = List[Tuple[Any, Hashable, Hashable]]


class AgreementMetricResult(BaseModel):
    """Container for the result of an agreement metric.

    It contains two fields, `metric_name` and `result` with the value of the metric.
    """

    metric_name: str
    result: float


def prepare_dataset_for_annotation_task(
    dataset: Union["FeedbackDataset", "RemoteFeedbackDataset"], question_name: str
) -> FormattedResponses:
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
                raise NotImplementedError(
                    "In order to use this functionality the records need to be assigned to a user."
                )

            value = response["value"]
            if question_type == RankingQuestion:
                value = "".join(value["value"])
            elif question_type == MultiLabelQuestion:
                value = "".join(value)

            formatted_responses.append((user_id, question_name, value))

    return formatted_responses


QUESTION_TO_DISTANCE = {
    LabelQuestion: binary_distance,
    MultiLabelQuestion: edit_distance,
    RatingQuestion: interval_distance,
    RankingQuestion: edit_distance,
}


class AgreementMetric:
    def __init__(self, dataset: "FeedbackDataset", question_name: str) -> None:
        """Initializes a `AgreementMetric` object to compute agreement metrics on
        a `FeedbackDataset` for a given question.

        Args:
            dataset: FeedbackDataset to compute the metrics.
            question_name: Name of the question for which we want to analyse the agreement.

        Raises:
            NotImplementedError: If the question type is not supported.
        """
        self._dataset = dataset
        self._question_name = question_name
        self._question_type = type(self._dataset.question_by_name(question_name))
        if self._question_type == TextQuestion:
            raise NotImplementedError(f"No metrics are defined currently for {self._question_type.__name__}")
        self._allowed_metrics = METRICS_PER_QUESTION[self._question_type]

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


class AnnotationTaskMetricBase(ABC):
    """Base class for Agreement metrics."""

    def __init__(self, annotated_dataset=None, distance_function: Callable = None) -> None:
        """
        Args:
            annotated_dataset: Annotated dataset as expected by the metric.
            distance_function: Distance function to use for the metric.
                Depending on the type of data we need a function to compute the distance.
                For example for binary data we can use the binary distance function,
                while RatingQuestion works with an interval distance as we are dealing with
                numeric values.
        """
        self._dataset = annotated_dataset
        self._distance_function = distance_function

    def compute(self, **kwargs) -> float:
        """General method to obtain the metric.

        Args:
            kwargs: Optional arguments that could be passed to the metric.

        Returns:
            metric: Metric result that will be stored in the `AgreementMetricResult`.
        """
        data = self._pre_process(self._dataset)
        return self._compute(data, **kwargs)

    def _pre_process(self, data, **kwargs) -> Any:
        """Optional data preprocessing. By default it just passes the data to the _compute method.

        Args:
            data: annotated dataset.
            kwargs: optional arguments to be passed to the metric.

        Returns:
            data: dataset prepared for the _compute method.
        """
        return data

    @abstractmethod
    def _compute(self, data, **kwargs):
        """Abstract method where the computation is done.

        Args:
            data: Data as expected for the given metric.
        """
        pass


class NLTKAnnotationTaskMetric(NLTKAnnotationTask, AnnotationTaskMetricBase):
    """Base class for metrics that use the nltk's AnnotationTask class."""

    def __init__(self, annotated_dataset=None, distance_function=binary_distance) -> None:
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
